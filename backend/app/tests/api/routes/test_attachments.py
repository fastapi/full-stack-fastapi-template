from datetime import datetime
import uuid
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.attachments import Attachment
from app.models.patients import Patient

def test_create_attachment(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # First create a patient to attach to
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    data = {
        "file_name": "test.pdf",
        "mime_type": "application/pdf",
        "storage_path": "patients/attachments/test.pdf",
        "description": "Test attachment",
        "patient_id": str(patient.id)
    }
    response = client.post(
        "/api/v1/attachments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["file_name"] == data["file_name"]
    assert content["mime_type"] == data["mime_type"]
    assert content["upload_url"] is not None
    assert "id" in content

def test_read_attachment_details(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # Create test patient
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Create test attachment
    attachment = Attachment(
        file_name="test.pdf",
        mime_type="application/pdf",
        storage_path="patients/attachments/test.pdf",
        description="Test attachment",
        patient_id=patient.id
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    response = client.get(
        f"/api/v1/attachments/{attachment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["file_name"] == attachment.file_name
    assert content["id"] == str(attachment.id)
    assert content["patient_id"] == str(attachment.patient_id)


def test_list_attachments(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # Create test patient
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Create test attachments
    attachment1 = Attachment(
        file_name="test1.pdf",
        mime_type="application/pdf",
        storage_path="patients/attachments/test1.pdf",
        patient_id=patient.id
    )
    attachment2 = Attachment(
        file_name="test2.pdf",
        mime_type="application/pdf",
        storage_path="patients/attachments/test2.pdf",
        patient_id=patient.id
    )
    db.add(attachment1)
    db.add(attachment2)
    db.commit()

    response = client.get(
        "/api/v1/attachments/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2


def test_attachment_not_found(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = client.get(
        f"/api/v1/attachments/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
