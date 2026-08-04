import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.extractors import extract_text_and_save_to_db
from app.core.s3 import generate_s3_url, upload_file_to_s3
from app.models import (
    Document,
    DocumentCreate,
    DocumentPublic,
    DocumentsPublic,
    DocumentUpdate,
    Message,
)

router = APIRouter(prefix="/documents", tags=["documents"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed MIME types for document uploads
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


@router.post("/", response_model=DocumentPublic)
def create_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,  # noqa: ARG001
    file: UploadFile = File(...),
) -> Any:
    # Validate MIME type
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type or 'unknown'}. Allowed types: PDF, DOC, DOCX, PPT, PPTX, TXT",
        )
    key = None

    try:
        key = upload_file_to_s3(file, str(current_user.id))
    except Exception as e:
        raise HTTPException(500, f"Failed to upload file. Error: {str(e)}")

    try:
        url = generate_s3_url(key)
    except Exception:
        raise HTTPException(500, f"Could not generate URL for file key: {key}")
    try:
        document_in = DocumentCreate(
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
            s3_url=url,
            s3_key=key,
        )
        document = Document.model_validate(
            document_in, update={"owner_id": current_user.id}
        )

        session.add(document)
        session.commit()
        session.refresh(document)

    except Exception:
        logging.exception(
            "Validation error: {e} Failed to create DocumentCreate instance. file: {file.filename}, content_type: {file.content_type}, size: {file.size}, s3_url: {url}, s3_key: {key}"
        )

    # 3. Kick off background job
    background_tasks.add_task(extract_text_and_save_to_db, key, str(document.id))
    return document


@router.get("/{id}", response_model=DocumentPublic)
def read_document(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get document by ID.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document


@router.get("/", response_model=DocumentsPublic)
def read_documents(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve documents.
    """
    count_statement = (
        select(func.count())
        .select_from(Document)
        .where(Document.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Document)
        .where(Document.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    documents = session.exec(statement).all()

    return DocumentsPublic(data=documents, count=count)


@router.put("/{id}", response_model=DocumentPublic)
def update_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    document_in: DocumentUpdate,
) -> Any:
    """
    Update an document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_in.model_dump(exclude_unset=True)
    document.sqlmodel_update(update_dict)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{id}")
def delete_document(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(document)
    session.commit()
    return Message(message="Document deleted successfully")
