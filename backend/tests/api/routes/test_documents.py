import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Document

def test_create_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    data = {"title": "Test Document", "description": "A test document"}
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content

def test_read_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    data = {"title": "Read Me", "description": "To be read"}
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    doc_id = response.json()["id"]
    
    response = client.get(
        f"{settings.API_V1_STR}/documents/{doc_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Read Me"

def test_create_document_version(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    data = {"title": "Versioned Doc", "description": "v1"}
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    doc_id = response.json()["id"]
    
    version_data = {"version_number": 1, "file_path": "/tmp/doc_v1.pdf"}
    response = client.post(
        f"{settings.API_V1_STR}/documents/{doc_id}/versions", headers=superuser_token_headers, json=version_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["version_number"] == 1
    assert content["document_id"] == doc_id
