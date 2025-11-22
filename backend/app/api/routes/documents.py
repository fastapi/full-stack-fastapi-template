import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import Json
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Document, DocumentCreate, DocumentRead, DocumentUpdate, DocumentVersion, DocumentVersionCreate, DocumentVersionRead, Message
from app.services.file_storage import storage_service

router = APIRouter()

@router.post("/", response_model=DocumentRead)
async def create_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    document_in: Json[DocumentCreate] = Form(...)
) -> Any:
    """
    Create new document with file.
    """
    # 1. Save file
    file_path = await storage_service.save_file(file, f"{uuid.uuid4()}_{file.filename}")
    
    # 2. Create Document
    document = Document.model_validate(document_in, update={"owner_id": current_user.id})
    session.add(document)
    session.commit()
    session.refresh(document)
    
    # 3. Create Initial Version
    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        file_path=file_path,
        created_by_id=current_user.id
    )
    session.add(version)
    session.commit()
    
    return document

@router.get("/{id}/content")
def download_document_content(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Download document content (latest version).
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Get latest version
    version = session.exec(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == id)
        .order_by(DocumentVersion.version_number.desc())
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Document has no content")
        
    file_path = storage_service.get_file_path(version.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
        
    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=f"{document.title}_{version.version_number}.pdf") # Assuming PDF or generic

@router.get("/{id}", response_model=DocumentRead)
def read_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get document by ID.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    # Check permissions if needed
    return document

@router.post("/{id}/versions", response_model=DocumentVersionRead)
def create_document_version(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, version_in: DocumentVersionCreate
) -> Any:
    """
    Add a new version to a document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    version = DocumentVersion.model_validate(version_in, update={"document_id": id, "created_by_id": current_user.id})
    session.add(version)
    session.commit()
    session.refresh(version)
    return version

@router.get("/{id}/versions", response_model=list[DocumentVersionRead])
def read_document_versions(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get all versions of a document.
    """
    statement = select(DocumentVersion).where(DocumentVersion.document_id == id)
    versions = session.exec(statement).all()
    return versions
