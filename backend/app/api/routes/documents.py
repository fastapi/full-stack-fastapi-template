from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.core.extractors import extract_text_and_save_to_db
from app.models import Document, DocumentCreate, DocumentPublic
from app.s3 import generate_s3_url, upload_file_to_s3

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentPublic)
def create_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,  # noqa: ARG001
    file: UploadFile = File(...),
) -> Any:
    key = None
    try:
        key = upload_file_to_s3(file, str(current_user.id))
    except Exception as e:
        raise HTTPException(500, f"Failed to upload file. Error: {str(e)}")

    try:
        url = generate_s3_url(key)
    except Exception:
        raise HTTPException(500, f"Could not generate URL for file key: {key}")

    document_in = DocumentCreate(
        filename=file.filename,
        content_type=file.content_type,
        size=file.size,
        s3_url=url,
    )

    document = Document.model_validate(
        document_in, update={"owner_id": current_user.id}
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    # 3. Kick off background job
    print("Document created, starting background task...")
    background_tasks.add_task(extract_text_and_save_to_db, url, str(document.id))
    return document
