import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import Document, AuditLog, Message
from app.tasks.retention import archive_document, dispose_document

router = APIRouter()

@router.post("/{id}/archive", response_model=Message)
async def manual_archive_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Manually archive a document (superuser or owner).
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Check ownership or superuser
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await archive_document(session, document)
    return Message(message="Document archived successfully")

@router.post("/{id}/dispose", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
async def manual_dispose_document(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Manually dispose of a document (GDPR-compliant deletion). Superuser only.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await dispose_document(session, document)
    return Message(message="Document disposed successfully")

@router.post("/{id}/force-unlock", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def force_unlock_document(
    *, session: SessionDep, id: uuid.UUID
) -> Any:
    """
    Force unlock a locked document. Admin/superuser only.
    """
    from app.models import DocumentLock
    from sqlmodel import select
    
    lock = session.exec(select(DocumentLock).where(DocumentLock.document_id == id)).first()
    if not lock:
        raise HTTPException(status_code=404, detail="Document is not locked")
        
    session.delete(lock)
    session.commit()
    
    return Message(message="Document unlocked successfully")
