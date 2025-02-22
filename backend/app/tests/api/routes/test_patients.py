from datetime import datetime
import uuid
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlmodel import Session

from app.models.patients import Patient

pytestmark = pytest.mark.asyncio

async def test_create_patient(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {
        "name": "Test Patient",
        "dob": "2000-01-01T00:00:00",
        "contact_info": "test@example.com",
        "medical_history": "No significant history"
    }
    response = await client.post(
        "/api/v1/patients/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["contact_info"] == data["contact_info"]
    assert "id" in content

async def test_read_patient(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: Session
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
    
    response = await client.get(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == patient.name
    assert content["id"] == str(patient.id)

async def test_read_patients(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: Session
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

    response = await client.get(
        "/api/v1/patients/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2

async def test_update_patient(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: Session
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
    response = await client.put(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["id"] == str(patient.id)

async def test_delete_patient(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    patient = Patient(
        name="Test Patient",
        dob=datetime(2000, 1, 1),
        contact_info="test@example.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    response = await client.delete(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify patient was deleted
    response = await client.get(
        f"/api/v1/patients/{patient.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404

async def test_patient_not_found(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = await client.get(
        f"/api/v1/patients/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
