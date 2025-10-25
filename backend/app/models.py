import uuid
from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    ingestions: list["Ingestion"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Extraction Status Enum
class ExtractionStatus(str, Enum):
    """Extraction pipeline status enum."""

    UPLOADED = "UPLOADED"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_COMPLETE = "OCR_COMPLETE"
    SEGMENTATION_PROCESSING = "SEGMENTATION_PROCESSING"
    SEGMENTATION_COMPLETE = "SEGMENTATION_COMPLETE"
    TAGGING_PROCESSING = "TAGGING_PROCESSING"
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# Shared properties for Ingestion
class IngestionBase(SQLModel):
    filename: str = Field(max_length=255, description="Original filename")
    file_size: int = Field(gt=0, description="File size in bytes")
    page_count: int | None = Field(default=None, description="Number of pages in PDF")
    mime_type: str = Field(max_length=100, description="MIME type (application/pdf)")
    status: ExtractionStatus = Field(default=ExtractionStatus.UPLOADED)


# Properties to receive via API on creation (not used for file upload)
class IngestionCreate(IngestionBase):
    pass


# Database model for extractions
class Ingestion(IngestionBase, table=True):
    __tablename__ = "extractions"  # Table name matches domain

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    presigned_url: str = Field(max_length=2048, description="Supabase presigned URL")
    storage_path: str = Field(max_length=512, description="Storage path in Supabase")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: "User" = Relationship(back_populates="ingestions")


# Properties to return via API
class IngestionPublic(IngestionBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    presigned_url: str
    uploaded_at: datetime


class IngestionsPublic(SQLModel):
    data: list[IngestionPublic]
    count: int
