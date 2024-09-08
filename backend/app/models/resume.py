from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from .datamodels import Resume


class UserResumes(SQLModel, table=True):
    '''
    UserResumes model to store the user resumes
    '''
    __tablename__:str = "user_resumes"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    blob_uri: str = Field()
    uploaded: bool = Field(default=False)
    uploaded_at: datetime = Field(default=datetime.utcnow)
    user: list["User"] = Relationship(back_populates="resumes")


class UserResumeJson(SQLModel, table=True):
    '''
    UserResumeJson model to store the user resumes in json format
    '''
    __tablename__:str = "user_resume_json"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    resume_json_data: Resume = Field(sa_type=JSONB, nullable=False)
    user: list["User"] = Relationship(back_populates="resumes_json")


class UserResumeUploadResponse(SQLModel):
    '''
    UserResumeUploadResponse model to store the user resume upload response
    '''
    presigned_url: str
    resume_id: UUID
