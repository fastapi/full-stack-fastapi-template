from typing import TYPE_CHECKING
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select
from sqlalchemy import Index
import uuid

if TYPE_CHECKING:
    from .attachments import Attachment

# Shared properties
class PatientBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    dob: datetime | None = Field(default=None)
    contact_info: str | None = Field(default=None, max_length=255)
    medical_history: str | None = Field(default=None, max_length=None)

# Properties to receive on patient creation
class PatientCreate(PatientBase):
    pass

# Properties to receive on patient update
class PatientUpdate(PatientBase):
    name: str | None = Field(default=None, min_length=1, max_length=255) # type: ignore

# Database model, database table inferred from class name
class Patient(PatientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attachments: list["Attachment"] = Relationship(back_populates="patient", cascade_delete=True)

    __table_args__ = (
        # define a fulltext index on medical_history
        Index(
            'ix_patient_medical_history_gin',
            'medical_history',
            postgresql_using='gin',
            postgresql_ops={'medical_history': 'gin_trgm_ops'}
        ),
    )

# Properties to return via API, id is always required
class PatientPublic(PatientBase):
    id: uuid.UUID

class PatientsPublic(SQLModel):
    data: list[PatientPublic]
    count: int
