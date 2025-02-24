from typing import Any
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy.dialects.postgresql.ext import to_tsquery
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.patients import (
    Patient,
    PatientCreate,
    PatientPublic,
    PatientsPublic,
    PatientUpdate,
)
from app.models.attachments import Attachment
from app.models import Message

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=PatientsPublic)
def read_patients(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    history_text: str = None, # full text search for medical history
    name_exact: str = None, # exact match for name
    name_text: str = None, # full text search for name
    has_attachment_mime_type: str = None, # filter by attachment MIME type
) -> Any:
    """
    Retrieve patients.
    """

    # assemble filters array from query parameters
    filters = []
    if history_text:
        filters.append(Patient.medical_history.op("@@")(to_tsquery(history_text)))
    if name_exact:
        filters.append(Patient.name == name_exact)
    if name_text:
        filters.append(Patient.name.op("@@")(to_tsquery(name_text)))
    if has_attachment_mime_type:
        filters.append(Patient.attachments.any(Attachment.mime_type == has_attachment_mime_type))

    count_statement = select(func.count()).select_from(Patient).filter(*filters)
    count = session.exec(count_statement).one()
    statement = select(Patient).filter(*filters).offset(skip).limit(limit)
    patients = session.exec(statement).all()

    return PatientsPublic(data=patients, count=count)


@router.get("/{id}", response_model=PatientPublic)
def read_patient(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get patient by ID.
    """
    patient = session.get(Patient, id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/", response_model=PatientPublic)
def create_patient(
    *, session: SessionDep, current_user: CurrentUser, patient_in: PatientCreate
) -> Any:
    """
    Create new patient.
    """
    patient = Patient.model_validate(patient_in)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.put("/{id}", response_model=PatientPublic)
def update_patient(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    patient_in: PatientUpdate,
) -> Any:
    """
    Update a patient.
    """
    patient = session.get(Patient, id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_dict = patient_in.model_dump(exclude_unset=True)
    patient.sqlmodel_update(update_dict)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.delete("/{id}")
def delete_patient(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a patient.
    """
    patient = session.get(Patient, id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(patient)
    session.commit()
    return Message(message="Patient deleted successfully")
