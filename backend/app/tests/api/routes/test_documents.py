import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch
from app.core.config import settings
from app.tests.utils.document import create_random_document
import io


def skip_test_create_document(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    '''Test creating a document with a file upload with the real S3 service.'''
    file_content = b"%PDF-1.4 test file content"

    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        files={
            "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert "id" in content, "actual response: " + str(content)
    # assert content["title"] == metadata["title"]
    # assert content["description"] == metadata["description"]
    # assert "id" in content
    # assert "owner_id" in content

def test_create_document(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    '''Test creating a document with a file upload using mocked S3.'''
    file_content = b"%PDF-1.4 test file content"

    with patch("app.api.routes.documents.upload_file_to_s3", return_value="document-slug"):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
            },
        )

    assert response.status_code == 200, f"Unexpected response: {response.content}"
    content = response.json()
    assert "id" in content, "actual response: " + str(content)
    assert "document-slug" in content["s3_url"], "S3 URL should match mocked value"
    assert content["filename"] == "example.pdf", "Filename should match uploaded file"
