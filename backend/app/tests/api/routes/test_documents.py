import io
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.document import create_random_document


def skip_test_create_document_real_s3(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with a file upload with the real S3 service."""
    file_content = b"%PDF-1.4 test file content"

    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        files={"file": ("example.pdf", io.BytesIO(file_content), "application/pdf")},
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
    """Test creating a document with a file upload using mocked S3."""
    file_content = b"%PDF-1.4 test file content"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value="document-slug"
    ):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
            },
        )

    assert response.status_code == 200, "Unexpected response status code"
    content = response.json()
    assert "id" in content, "actual response: " + str(content)
    assert "document-slug" in content["s3_url"], "S3 URL should match mocked value"
    assert content["filename"] == "example.pdf", "Filename should match uploaded file"


def test_read_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["size"] == document.size
    assert content["filename"] == document.filename
    assert content["content_type"] == document.content_type
    assert content["s3_url"] == document.s3_url
    assert content["s3_key"] == document.s3_key
    assert content["id"] == str(document.id)
    assert content["owner_id"] == str(document.owner_id)


def test_read_documents(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_document(db)
    create_random_document(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
