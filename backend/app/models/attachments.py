import uuid

from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from .patients import Patient

# Shared properties
class AttachmentBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    dob: datetime | None = Field(default=None, max_length=255)
    contact_info: str | None = Field(default=None, max_length=255)
    medical_history: str | None = Field(default=None, max_length=255)

# Properties to receive on attachment creation
class AttachmentCreate(AttachmentBase):
    pass

# Properties to receive on attachment update
class AttachmentUpdate(AttachmentBase):
    name: str | None = Field(default=None, min_length=1, max_length=255) # type: ignore

# Database model, database table inferred from class name
class Attachment(AttachmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patient_id: uuid.UUID = Field(
        foreign_key="patient.id", nullable=False, ondelete="CASCADE"
    )
    patient: Patient | None = Relationship(back_populates="attachments")

# Properties to return via API, id is always required
class AttachmentPublic(AttachmentBase):
    id: uuid.UUID

class AttachmentsPublic(SQLModel):
    data: list[AttachmentPublic]
    count: int
