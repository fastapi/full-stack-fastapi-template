import re
import uuid

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from .patients import Patient

mime_type_pattern = re.compile(r'^[a-zA-Z0-9]+/[a-zA-Z0-9\-.+]+$')

# Shared properties
class AttachmentBase(SQLModel):
    file_name: str = Field(min_length=1, max_length=None)
    mime_type: str | None = Field(default=None, max_length=255)

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v):
        if v is None:
            return v
        if not mime_type_pattern.match(v):
            raise ValueError("Invalid MIME type format")
        return v

# Properties to receive on attachment creation
class AttachmentCreate(AttachmentBase):
    patient_id: uuid.UUID = Field(nullable=False)

# Properties to receive on attachment update
class AttachmentUpdate(AttachmentBase):
    pass

# Database model, database table inferred from class name
class Attachment(AttachmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(
        foreign_key="patient.id", nullable=False, ondelete="CASCADE"
    )
    patient: Patient | None = Relationship(back_populates="attachments")

    # get the blob storage path, which is assembled from the patient
    # id and the attachment ID
    @property
    def storage_path(self):
        return f"patients/{self.patient_id}/attachments/{self.id}"

# Properties to return via API, id is always required
class AttachmentPublic(AttachmentBase):
    id: uuid.UUID
    patient_id: uuid.UUID = Field(nullable=False)

class AttachmentCreatePublic(AttachmentPublic):
    upload_url: str = Field(nullable=False) # presigned URL for uploading to blob storage

class AttachmentsPublic(SQLModel):
    data: list[AttachmentPublic]
    count: int
