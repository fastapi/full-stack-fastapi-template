import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.attachments import (
    Attachment,
    AttachmentCreate,
    AttachmentPublic,
    AttachmentsPublic,
    AttachmentUpdate,
)
from app.models import Message

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/", response_model=AttachmentsPublic)
def read_attachments(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve attachments.
    """
    count_statement = select(func.count()).select_from(Attachment)
    count = session.exec(count_statement).one()
    statement = select(Attachment).offset(skip).limit(limit)
    attachments = session.exec(statement).all()

    return AttachmentsPublic(data=attachments, count=count)


@router.get("/{id}", response_model=AttachmentPublic)
def read_attachment(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get attachment by ID.
    """
    attachment = session.get(Attachment, id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.post("/", response_model=AttachmentPublic)
def create_attachment(
    *, session: SessionDep, current_user: CurrentUser, attachment_in: AttachmentCreate
) -> Any:
    """
    Create new attachment.
    """
    attachment = Attachment.model_validate(attachment_in)
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


@router.put("/{id}", response_model=AttachmentPublic)
def update_attachment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    attachment_in: AttachmentUpdate,
) -> Any:
    """
    Update an attachment.
    """
    attachment = session.get(Attachment, id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    update_dict = attachment_in.model_dump(exclude_unset=True)
    attachment.sqlmodel_update(update_dict)
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


@router.delete("/{id}")
def delete_attachment(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an attachment.
    """
    attachment = session.get(Attachment, id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    session.delete(attachment)
    session.commit()
    return Message(message="Attachment deleted successfully")
