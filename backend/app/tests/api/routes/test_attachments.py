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
        "filename": "test.pdf",
        "content_type": "application/pdf",
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
    assert content["filename"] == data["filename"]
    assert content["content_type"] == data["content_type"]
    assert "id" in content

def test_read_attachment(
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
        filename="test.pdf",
        content_type="application/pdf",
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
    assert content["filename"] == attachment.filename
    assert content["id"] == str(attachment.id)

def test_read_attachments(
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
        filename="test1.pdf",
        content_type="application/pdf",
        patient_id=patient.id
    )
    attachment2 = Attachment(
        filename="test2.pdf",
        content_type="application/pdf",
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

def test_update_attachment(
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
        filename="test.pdf",
        content_type="application/pdf",
        patient_id=patient.id
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    data = {"filename": "updated.pdf"}
    response = client.put(
        f"/api/v1/attachments/{attachment.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == data["filename"]
    assert content["id"] == str(attachment.id)

def test_delete_attachment(
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
        filename="test.pdf",
        content_type="application/pdf",
        patient_id=patient.id
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    response = client.delete(
        f"/api/v1/attachments/{attachment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify attachment was deleted
    response = client.get(
        f"/api/v1/attachments/{attachment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404

def test_attachment_not_found(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = client.get(
        f"/api/v1/attachments/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
