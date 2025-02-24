import logging
from typing import Any
import uuid

import boto3
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, s3_client
from app.core.config import settings
from app.models.attachments import (
    Attachment,
    AttachmentCreate,
    AttachmentCreatePublic,
    AttachmentPublic,
    AttachmentsPublic,
    AttachmentUpdate,
)
from app.models import Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/", response_model=AttachmentsPublic)
def read_attachments(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve list of all attachments.
    """
    count_statement = select(func.count()).select_from(Attachment)
    count = session.exec(count_statement).one()
    statement = select(Attachment).offset(skip).limit(limit)
    attachments = session.exec(statement).all()

    return AttachmentsPublic(data=attachments, count=count)

@router.get("/{id}/content")
def read_attachment_content(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get attachment content by ID.
    """
    attachment = session.get(Attachment, id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_S3_ATTACHMENTS_BUCKET,
                "Key": attachment.storage_path,
                "ContentDisposition": f"attachment; filename={attachment.file_name}",
            },
            ExpiresIn=3600,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Could not generate presigned URL")

    return RedirectResponse(status_code=302, url=presigned_url)


@router.get("/{id}", response_model=AttachmentPublic)
def read_attachment(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get attachment details by ID.
    """
    attachment = session.get(Attachment, id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.post("/", response_model=AttachmentCreatePublic)
def create_attachment(
    *, session: SessionDep, current_user: CurrentUser, attachment_in: AttachmentCreate
) -> Any:
    """
    Create a new attachment.
    """
    attachment = Attachment.model_validate(attachment_in)
    session.add(attachment)
    session.commit()
    session.refresh(attachment)

    try:
        presigned_upload_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_S3_ATTACHMENTS_BUCKET,
                "Key": attachment.storage_path,
                "ContentDisposition": f"attachment; filename={attachment.file_name}",
            },
            ExpiresIn=3600,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Could not generate presigned URL")

    resmodel = AttachmentCreatePublic.model_validate(
        attachment, update={"upload_url": presigned_upload_url}
    )

    return resmodel
