from typing import Any

from azure.storage.blob import BlobSasPermissions
from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import (
    CurrentUser,
    SessionDep,
)
from app.models import Message, UserResumeJson, UserResumes, UserResumeUploadResponse
from app.models.datamodels import Resume
from app.utils import generate_azure_presigned_url, generate_blob_name

router = APIRouter()


@router.get("/download")
async def download_user_resume(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Download User Resume
    """
    query = (
        select(UserResumes)
        .where(UserResumes.user_id == current_user.id)
        .order_by(UserResumes.uploaded_at.desc())
    )
    user_resume_obj = session.exec(query).first()
    if user_resume_obj:
        presigned_url = generate_azure_presigned_url(
            blob_name=user_resume_obj.blob_uri,
            permission=BlobSasPermissions(read=True),
            expiry_duration=5,
        )
        return {"presigned_url": presigned_url}
    return {"error": "Resume not found"}


@router.post("/upload")
async def upload_user_resume(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Upload User Resume
    """
    try:
        with session.begin():
            blob_name = generate_blob_name(current_user.id)
            presigned_url = generate_azure_presigned_url(
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True, write=True),
                expiry_duration=5,
            )
            user_resume_obj = UserResumes(
                user_id=current_user.id,
                blob_uri=blob_name,
            )
            session.add(user_resume_obj)
            session.commit()
            return {"presigned_url": presigned_url}
    except Exception as e:
        session.rollback()
        return {"error": str(e)}


@router.put("/update-status")
async def update_user_resume_status(
    session: SessionDep, current_user: CurrentUser, upload_in: UserResumeUploadResponse
) -> Message:
    """
    Update User Resume Upload Status
    """
    try:
        query = select(UserResumes).where(UserResumes.id == upload_in.resume_id)
        user_resume_obj = session.exec(query).first()
        if user_resume_obj:
            user_resume_obj.uploaded = True
            session.add(user_resume_obj)
            session.commit()
            return Message(message="Resume Upload was successful")
        else:
            return Message(message="Resume not found")
    except Exception as e:
        session.rollback()
        return Message(message=f"Resume Upload failed: {e}")


@router.post("/upload-json", response_model=Message)
async def upload_user_resume_json(
    session: SessionDep, current_user: CurrentUser, resume_json: Resume
) -> Message:
    """
    Upload User Resume JSON
    """
    try:
        user_resume_obj = UserResumeJson(
            user_id=current_user.id, resume_json_data=resume_json.dict()
        )
        session.add(user_resume_obj)
        session.commit()
        return Message(message="Resume JSON Upload was successfull")
    except Exception as e:
        session.rollback()
        return Message(message=f"Resume JSON Upload failed: {e}")
