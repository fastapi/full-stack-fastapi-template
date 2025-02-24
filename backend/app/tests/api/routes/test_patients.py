from datetime import datetime
import uuid
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.patients import Patient

def test_create_patient(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {
        "name": "Test Patient",
        "dob": "2000-01-01T00:00:00",
        "contact_info": "test@example.com",
        "medical_history": "No significant history"
    }
    response = client.post(
        "/api/v1/patients/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["contact_info"] == data["contact_info"]
    assert "id" in content

def test_read_patient(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com",
        medical_history="No significant history"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    response = client.get(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == patient.name
    assert content["id"] == str(patient.id)

def test_read_patients(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    patient1 = Patient(
        name="Test Patient 1",
        dob=datetime(2000, 1, 1),
        contact_info="test1@example.com"
    )
    patient2 = Patient(
        name="Test Patient 2",
        dob=datetime(2000, 1, 2),
        contact_info="test2@example.com"
    )
    db.add(patient1)
    db.add(patient2)
    db.commit()

    response = client.get(
        "/api/v1/patients/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2

def test_read_patients_history_search(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # Create test patients with different medical histories
    patient1 = Patient(
        name="Test Patient 1",
        dob=datetime(2000, 1, 1),
        contact_info="test1@example.com",
        medical_history="Patient has a fulltext history of asthma"
    )
    patient2 = Patient(
        name="Test Patient 2",
        dob=datetime(2000, 1, 2),
        contact_info="test2@example.com",
        medical_history="Patient has a fulltext history of diabetes"
    )
    patient3 = Patient(
        name="Test Patient 3",
        dob=datetime(2000, 1, 3),
        contact_info="test3@example.com",
        medical_history="No significant fulltext medical history"
    )
    db.add(patient1)
    db.add(patient2)
    db.add(patient3)
    db.commit()

    # Test searching for patients with asthma
    response = client.get(
        "/api/v1/patients/?history_text=asthma",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert content["data"][0]["medical_history"] == patient1.medical_history

    # Test searching for patients with any history
    response = client.get(
        "/api/v1/patients/?history_text=fulltext",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 3

def test_read_patients_name_exact(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # Create test patients with different names
    patient1 = Patient(
        name="Bob Smith",
        dob=datetime(2000, 1, 1),
        contact_info="bob@example.com"
    )
    patient2 = Patient(
        name="Bob Doe",
        dob=datetime(2000, 1, 2),
        contact_info="doe@example.com"
    )
    db.add(patient1)
    db.add(patient2)
    db.commit()

    # Test exact name match
    response = client.get(
        "/api/v1/patients/?name_exact=Bob Smith",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert content["data"][0]["name"] == "Bob Smith"

def test_read_patients_name_text(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    # Create test patients with different names
    patient1 = Patient(
        name="John Smith",
        dob=datetime(2000, 1, 1),
        contact_info="john@example.com"
    )
    patient2 = Patient(
        name="John Doe",
        dob=datetime(2000, 1, 2),
        contact_info="doe@example.com"
    )
    patient3 = Patient(
        name="Jane Wilson",
        dob=datetime(2000, 1, 3),
        contact_info="jane@example.com"
    )
    db.add(patient1)
    db.add(patient2)
    db.add(patient3)
    db.commit()

    # Test full text search on name
    response = client.get(
        "/api/v1/patients/?name_text=John",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    assert all("John" in patient["name"] for patient in content["data"])

def test_read_patients_attachment_filter(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    from app.models.attachments import Attachment

    # Create test patients with different attachments
    patient1 = Patient(
        name="Test Patient 1",
        dob=datetime(2000, 1, 1),
        contact_info="test1@example.com"
    )
    patient2 = Patient(
        name="Test Patient 2",
        dob=datetime(2000, 1, 2),
        contact_info="test2@example.com"
    )
    db.add(patient1)
    db.add(patient2)
    db.commit()
    db.refresh(patient1)
    db.refresh(patient2)

    # Add different types of attachments
    attachment1 = Attachment(
        file_name="test1.bam",
        mime_type="application/x-bam",
        patient_id=patient1.id
    )
    attachment2 = Attachment(
        file_name="test.cram",
        mime_type="application/x-cram",
        patient_id=patient2.id
    )
    db.add(attachment1)
    db.add(attachment2)
    db.commit()

    # Test filtering by attachment MIME type
    response = client.get(
        "/api/v1/patients/?has_attachment_mime_type=application/x-bam",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert content["data"][0]["id"] == str(patient1.id)

def test_update_patient(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    data = {"name": "Updated Patient Name"}
    response = client.put(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["id"] == str(patient.id)

def test_delete_patient(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    response = client.delete(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify patient was deleted
    response = client.get(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404

def test_patient_not_found(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = client.get(
        f"/api/v1/patients/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
