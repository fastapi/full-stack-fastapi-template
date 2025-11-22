import uuid
import shutil
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Document, DocumentLock, DocumentVersion, 
    DocumentWorkflowInstance, Workflow, WorkflowStep, WorkflowAction,
    Message
)
from app.services.file_storage import storage_service

router = APIRouter()

@router.post("/{id}/checkout", response_model=Message)
def checkout_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Checkout a document for editing (locks it).
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if already locked
    lock = session.exec(select(DocumentLock).where(DocumentLock.document_id == id)).first()
    if lock:
        # Check if expired (e.g. 24 hours)
        if lock.expires_at and lock.expires_at < datetime.utcnow():
            session.delete(lock)
            session.commit()
        elif lock.locked_by_id != current_user.id:
            raise HTTPException(status_code=400, detail="Document is already locked by another user")
        else:
            return Message(message="Document already checked out by you")
            
    # Create lock
    lock = DocumentLock(
        document_id=id,
        locked_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(lock)
    session.commit()
    return Message(message="Document checked out successfully")

@router.post("/{id}/checkin", response_model=DocumentVersion)
async def checkin_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    file: UploadFile = File(...),
    comment: str = Form(None)
) -> Any:
    """
    Checkin a document (uploads new version and unlocks).
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Verify lock
    lock = session.exec(select(DocumentLock).where(DocumentLock.document_id == id)).first()
    if not lock:
        raise HTTPException(status_code=400, detail="Document is not checked out")
    if lock.locked_by_id != current_user.id:
        raise HTTPException(status_code=400, detail="Document is locked by another user")
        
    # Save file
    file_path = await storage_service.save_file(file, f"{uuid.uuid4()}_{file.filename}")
    
    # Determine next version number
    last_version = session.exec(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == id)
        .order_by(DocumentVersion.version_number.desc())
    ).first()
    next_version = (last_version.version_number + 1) if last_version else 1
    
    # Create version
    version = DocumentVersion(
        document_id=id,
        version_number=next_version,
        file_path=file_path,
        created_by_id=current_user.id
    )
    session.add(version)
    
    # Remove lock
    session.delete(lock)
    
    session.commit()
    session.refresh(version)
    return version

@router.post("/{id}/submit", response_model=DocumentWorkflowInstance)
def submit_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, workflow_id: uuid.UUID
) -> Any:
    """
    Submit document to a workflow.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Get first step
    first_step = session.exec(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_id == workflow_id)
        .order_by(WorkflowStep.order)
    ).first()
    
    if not first_step:
        raise HTTPException(status_code=400, detail="Workflow has no steps")
        
    # Create instance
    instance = DocumentWorkflowInstance(
        document_id=id,
        workflow_id=workflow_id,
        current_step_id=first_step.id,
        status="in_progress"
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    
    # Update document status
    document.status = "In Review"
    document.current_workflow_id = instance.id
    session.add(document)
    session.commit()
    
    return instance

@router.post("/{id}/rollback/{version_id}", response_model=DocumentVersion)
async def rollback_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, version_id: uuid.UUID
) -> Any:
    """
    Rollback document to a specific version (creates new version from old file).
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    target_version = session.get(DocumentVersion, version_id)
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    if target_version.document_id != id:
        raise HTTPException(status_code=400, detail="Version does not belong to this document")
        
    # Check if locked
    lock = session.exec(select(DocumentLock).where(DocumentLock.document_id == id)).first()
    if lock and lock.locked_by_id != current_user.id:
        raise HTTPException(status_code=400, detail="Document is locked by another user")
        
    # Create new version from old file
    # We copy the file to a new path to avoid issues if old file is deleted (though we shouldn't delete old versions)
    # For local storage, we can just copy.
    
    old_path = storage_service.get_file_path(target_version.file_path)
    if not old_path.exists():
         raise HTTPException(status_code=404, detail="Version file not found on server")
         
    filename = old_path.name
    new_filename = f"{uuid.uuid4()}_rollback_{filename}"
    
    # We need to read old file and save as new. 
    # Since storage_service.save_file takes UploadFile, we might need a lower level method or mock UploadFile.
    # Let's add copy_file to storage_service or just do it manually here since we are in backend.
    # Better to add copy method to storage service.
    
    # For now, manual copy using shutil
    new_path = storage_service.storage_dir / new_filename
    shutil.copy2(old_path, new_path)
    
    # Determine next version number
    last_version = session.exec(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == id)
        .order_by(DocumentVersion.version_number.desc())
    ).first()
    next_version = (last_version.version_number + 1) if last_version else 1
    
    version = DocumentVersion(
        document_id=id,
        version_number=next_version,
        file_path=str(new_path),
        created_by_id=current_user.id
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    
    return version
