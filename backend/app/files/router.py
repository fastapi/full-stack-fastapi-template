import uuid

from fastapi import APIRouter, Form, HTTPException, Response, UploadFile
from sqlalchemy import desc
from sqlmodel import select

from app.aws.client import upload_file_to_r2
from app.backend_pre_start import logger
from app.files.crud import (
    create_file,
    delete_file,
    get_file_job_by_file_id,
    update_file_job,
)
from app.files.dependencies import CurrentUser, SessionDep
from app.files.models import File, FileJob
from app.files.schemas import (
    FileCreate,
    FileJobPublic,
    FilePreviewResponse,
    FilePublic,
    FilesStatusRequest,
    FileWithJobPublic,
)
from app.files.service import (
    download_file,
    download_file_with_accounting_code,
    get_preview_data
)
from app.ocrs.constants import OcrJobStatus, OcrModel
from app.ocrs.service import (
    fetch_ocr_table_pages,
    get_ocr_job_status,
    post_ocr_jobs,
)

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/models", response_model=list[str])
def list_ocr_models():
    """List the OCR models a user can choose from when parsing a document."""
    return sorted(OcrModel.ALL)

@router.post("/", response_model=FilePublic)
def upload_file_endpoint(
    session: SessionDep,
    user: CurrentUser,
    file: UploadFile,  # noqa: B008
    model: str | None = Form(default=None),
):
    """
    Upload a file to R2/S3 storage.

    `model` selects which PaddleOCR model parses the document. When omitted,
    the configured default (settings.OCR_MODEL) is used.
    """
    if model is not None and model not in OcrModel.ALL:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported model '{model}'. Allowed: {sorted(OcrModel.ALL)}",
        )

    file_bytes = file.file.read()
    file_name = file.filename or "upload"
    file_type = file.content_type or "application/octet-stream"
    file_create = FileCreate(filename=file_name, content_type=file_type, size=len(file_bytes), url="")
    file_result = create_file(session=session, file_in=file_create, user_id=user.id)
    key = user.email + "/" + str(file_result.id) + "/" + file_name

    try:
         # upload to r2
        r2_result = upload_file_to_r2(
            key=key,  # Use DB record ID for unique key
            data=file_bytes,
            content_type=file.content_type,
            presign=True
        )

    # enqueue OCR job
        if not r2_result.get("IsSuccess"):
            delete_file(session=session, file_id=file_result.id)  # Clean up DB record on failure
            raise HTTPException(status_code=500, detail="Failed to upload file to R2")

        logger.info(f"File {file_result.id} uploaded to R2 successfully, URL: {r2_result['PresignedURL']}")
        post_ocr_jobs(session=session, file=file_result, file_url=r2_result["PresignedURL"], model=model)

        return file_result
    except Exception as exc:
        delete_file(session=session, file_id=file_result.id)  # Clean up DB record on failure
        logger.error(f"Error handling uploaded file {file_name}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.put("/{file_id}", response_model=FileJobPublic)
def update_file_job_status_endpoint(
    file_id: uuid.UUID,
    job_status: str,
    session: SessionDep,
):
    """
    Update the job status for a file based on OCR job updates.
    """
    file_job = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job:
        raise HTTPException(status_code=404, detail="FileJob not found")
    updated = update_file_job(session=session, file_job=file_job, state=job_status)
    return updated

@router.get("/{file_id}/status", response_model=FileJobPublic)
def get_file_status(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Get the current OCR job status for a file by polling the OCR API.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    get_ocr_job_status(file=file, session=session, user=user)  # Poll & persist latest state

    file_job = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job:
        raise HTTPException(status_code=404, detail="No job found for this file")
    return file_job

@router.get("/{file_id}/job", response_model=FileJobPublic)
def get_file_job(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Get the FileJob record for a given file, containing detailed OCR progress info.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    file_job: FileJob | None = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job:
        raise HTTPException(status_code=404, detail="No job found for this file")
    return file_job


@router.get('/', response_model=list[FileWithJobPublic])
def list_files(session: SessionDep, user: CurrentUser, skip: int = 0, limit: int = 0):
    """
    List all files uploaded by the current user, each enriched with its FileJob.
    """
    user_id = user.id
    if limit <= 0:
        statement = select(File).where(File.user_id == user_id).order_by(desc(File.created_at))  # ty:ignore[invalid-argument-type]
    else:
        statement = select(File).where(File.user_id == user_id).order_by(desc(File.created_at)).offset(skip).limit(limit)  # ty:ignore[invalid-argument-type]

    files = session.exec(statement).all()

    result: list[FileWithJobPublic] = []
    for f in files:
        file_job = get_file_job_by_file_id(session=session, file_id=f.id)

        # Refresh any still-processing job by polling the OCR API via its job_id.
        if file_job and file_job.state in (OcrJobStatus.PENDING, OcrJobStatus.RUNNING):
            try:
                get_ocr_job_status(file=f, session=session, user=user)
                file_job = get_file_job_by_file_id(session=session, file_id=f.id)
            except Exception as exc:
                logger.error(f"Error refreshing OCR status for file {f.id}: {exc}")

        job_public: FileJobPublic | None = FileJobPublic.model_validate(file_job) if file_job else None
        result.append(FileWithJobPublic.model_validate(f, update={"job": job_public}))

    return result

@router.post("/{file_id}/download", response_class=Response)
def download_table_excel_file(file_id: uuid.UUID, type: str, session: SessionDep, user: CurrentUser,):
    """
    Stream an Excel file built from the OCR result JSON stored in R2.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    file_job = get_file_job_by_file_id(session=session, file_id=file_id)

    if not file_job or file_job.state != "done":
        raise HTTPException(status_code=400, detail="OCR job is not done yet")

    logger.info(f"Preparing to stream file {file_id} for user {user.email} with requested type {type}")
    excel_bytes, content_disposition = download_file(session=session, file=file, type=type)
    media_type = {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "json": "application/json",
        "html": "text/html",
    }.get(type, "application/octet-stream")

    return Response(
        content=excel_bytes,
        media_type=media_type,
        headers={"Content-Disposition": content_disposition},
    )


@router.post("/{file_id}/download/new", response_class=Response)
def download_new_version_excel(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Generate and return a new version of the Excel file created by the standard
    download endpoint. This will fetch the existing generated Excel bytes, write
    them to a temporary file, call `get_gemini_response_for_file` to produce a
    modified xlsx, and stream that back to the client.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    file_job = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job or file_job.state != "done":
        raise HTTPException(status_code=400, detail="OCR job is not done yet")
    try:
        ex_bytes, content_disposition = download_file_with_accounting_code(session=session, file=file, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(
        content=ex_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": content_disposition},
    )

@router.post("/batch/status", response_model=list[FileJobPublic])
def get_files_batch_status(
    body: FilesStatusRequest,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Accept a list of file IDs, refresh each file's OCR job status via the OCR API,
    and return the updated list of FileJob records.
    """
    file_jobs: list[FileJob] = []
    for file_id in body.file_ids:
        file = session.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        if file.user_id != user.id:
            raise HTTPException(status_code=403, detail=f"Not authorized to access file {file_id}")

        try:
            get_ocr_job_status(file=file, session=session, user=user)
        except Exception as exc:
            logger.error(f"Error refreshing OCR status for file {file_id}: {exc}")

        file_job = get_file_job_by_file_id(session=session, file_id=file_id)
        if file_job:
            file_jobs.append(file_job)

    return file_jobs

@router.get("/{file_id}/preview", response_model=FilePreviewResponse)
def preview_file_result(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Fetch the parsed OCR result for a file from its stored ``json_url`` and
    return the extracted table as JSON (``columns`` + ``rows``), ready to render
    in the front end. This is the same table data the download endpoint exports.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    file_job = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job or file_job.state != OcrJobStatus.DONE:
        raise HTTPException(status_code=400, detail="OCR job is not done yet")
    if not file_job.json_url:
        raise HTTPException(status_code=400, detail="No result data available for this file")

    try:
        columns, rows = get_preview_data(file_job)
    except Exception as exc:
        logger.error("Failed to fetch OCR preview for file %s: %s", file_id, exc)
        raise HTTPException(status_code=502, detail="Failed to load result data") from exc

    return FilePreviewResponse(
        file_id=file.id,
        filename=file.filename,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        markdown_url=file_job.markdown_url,
    )
