import io
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.document import create_random_document  # type: ignore
from tests.utils.user import get_bootstrap_user


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


def test_read_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db, user=get_bootstrap_user(db))
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
    assert "status" in content
    assert content["status"] in ["processing", "ready", "failed"]


def test_read_documents(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    owner = get_bootstrap_user(db)
    create_random_document(db, user=owner)
    create_random_document(db, user=owner)
    response = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db, user=get_bootstrap_user(db))
    data = {"s3_key": "UpdatedKey"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["size"] == document.size
    assert content["filename"] == document.filename
    assert content["content_type"] == document.content_type
    assert content["s3_url"] == document.s3_url
    assert content["s3_key"] == "UpdatedKey"
    assert content["id"] == str(document.id)
    assert content["owner_id"] == str(document.owner_id)
    assert "status" in content
    assert content["status"] in ["processing", "ready", "failed"]


def test_delete_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db, user=get_bootstrap_user(db))
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Document deleted successfully"


def test_delete_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_delete_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_create_document_success(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with a file upload using mocked S3."""
    file_content = b"%PDF-1.4 test file content"
    mock_key = "documents/user-id/test-uuid.pdf"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value=mock_key
    ), patch(
        "app.api.routes.documents.generate_s3_url",
        return_value=f"https://bucket.s3.amazonaws.com/{mock_key}",
    ), patch("app.api.routes.documents.extract_text_and_save_to_db"):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
            },
        )

    assert (
        response.status_code == 200
    ), f"Unexpected status: {response.status_code}, body: {response.text}"
    content = response.json()
    assert "id" in content
    assert content["filename"] == "example.pdf"
    assert content["content_type"] == "application/pdf"
    assert content["size"] == len(file_content)
    assert mock_key in content["s3_url"]
    assert content["s3_key"] == mock_key
    assert "status" in content
    assert content["status"] == "processing"  # New documents start as processing


def test_create_document_docx_success(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with a DOCX file upload."""
    file_content = b"DOCX file content"
    mock_key = "documents/user-id/test-uuid.docx"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value=mock_key
    ), patch(
        "app.api.routes.documents.generate_s3_url",
        return_value=f"https://bucket.s3.amazonaws.com/{mock_key}",
    ), patch("app.api.routes.documents.extract_text_and_save_to_db"):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": (
                    "example.docx",
                    io.BytesIO(file_content),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "example.docx"
    assert (
        content["content_type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert content["status"] == "processing"


def test_create_document_pptx_success(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with a PPTX file upload."""
    file_content = b"PPTX file content"
    mock_key = "documents/user-id/test-uuid.pptx"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value=mock_key
    ), patch(
        "app.api.routes.documents.generate_s3_url",
        return_value=f"https://bucket.s3.amazonaws.com/{mock_key}",
    ), patch("app.api.routes.documents.extract_text_and_save_to_db"):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": (
                    "example.pptx",
                    io.BytesIO(file_content),
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            },
        )

    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "example.pptx"
    assert (
        content["content_type"]
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert content["status"] == "processing"


def test_create_document_txt_success(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with a TXT file upload."""
    file_content = b"Plain text file content"
    mock_key = "documents/user-id/test-uuid.txt"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value=mock_key
    ), patch(
        "app.api.routes.documents.generate_s3_url",
        return_value=f"https://bucket.s3.amazonaws.com/{mock_key}",
    ), patch("app.api.routes.documents.extract_text_and_save_to_db"):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={"file": ("example.txt", io.BytesIO(file_content), "text/plain")},
        )

    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "example.txt"
    assert content["content_type"] == "text/plain"
    assert content["status"] == "processing"


def test_create_document_invalid_mime_type(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document with an invalid MIME type."""
    file_content = b"Invalid file content"

    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        files={"file": ("example.jpg", io.BytesIO(file_content), "image/jpeg")},
    )

    assert response.status_code == 400
    content = response.json()
    assert "Unsupported file type" in content["detail"]


def test_create_document_s3_upload_failure(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document when S3 upload fails."""
    file_content = b"%PDF-1.4 test file content"

    with patch(
        "app.api.routes.documents.upload_file_to_s3",
        side_effect=Exception("S3 upload failed"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
            },
        )

    assert response.status_code == 500
    content = response.json()
    assert "Failed to upload file" in content["detail"]


def test_create_document_url_generation_failure(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a document when URL generation fails."""
    file_content = b"%PDF-1.4 test file content"
    mock_key = "documents/user-id/test-uuid.pdf"

    with patch(
        "app.api.routes.documents.upload_file_to_s3", return_value=mock_key
    ), patch(
        "app.api.routes.documents.generate_s3_url",
        side_effect=Exception("URL generation failed"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            files={
                "file": ("example.pdf", io.BytesIO(file_content), "application/pdf")
            },
        )

    assert response.status_code == 500
    content = response.json()
    assert "Could not generate URL" in content["detail"]


def test_read_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test reading a document that doesn't exist."""
    non_existent_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/documents/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_read_document_permission_denied(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a document owned by another user."""
    from tests.utils.user import create_random_user  # type: ignore

    # Create document owned by a different user
    other_user = create_random_user(db)
    document = create_random_document(db, user=other_user)

    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_documents_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading documents with pagination."""
    # Create multiple documents owned by the authenticated user
    owner = get_bootstrap_user(db)
    for _ in range(5):
        create_random_document(db, user=owner)

    # Test with skip and limit
    response = client.get(
        f"{settings.API_V1_STR}/documents/?skip=0&limit=2",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) <= 2
    assert content["count"] >= 5

    # Test second page
    response = client.get(
        f"{settings.API_V1_STR}/documents/?skip=2&limit=2",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) <= 2


def test_update_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating a document that doesn't exist."""
    non_existent_id = uuid.uuid4()
    data = {"filename": "updated.pdf"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{non_existent_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_update_document_permission_denied(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating a document owned by another user."""
    from tests.utils.user import create_random_user  # type: ignore

    # Create document owned by a different user
    other_user = create_random_user(db)
    document = create_random_document(db, user=other_user)

    data = {"filename": "updated.pdf"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_update_document_partial_update(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating only some fields of a document."""
    document = create_random_document(db, user=get_bootstrap_user(db))
    original_size = document.size

    # Update only filename
    data = {"filename": "updated-filename.pdf"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "updated-filename.pdf"
    # Other fields should remain unchanged
    assert content["size"] == original_size


def test_update_document_multiple_fields(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating multiple fields of a document."""
    document = create_random_document(db, user=get_bootstrap_user(db))

    data = {
        "filename": "updated-multiple.pdf",
        "s3_key": "updated/key/path.pdf",
    }
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "updated-multiple.pdf"
    assert content["s3_key"] == "updated/key/path.pdf"
    assert "status" in content  # Status should still be present


def test_read_document_with_processing_status(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a document with processing status."""
    from app.models import DocumentStatus

    document = create_random_document(
        db, user=get_bootstrap_user(db), status=DocumentStatus("processing")
    )
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "processing"


def test_read_document_with_ready_status(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a document with ready status."""
    from app.models import DocumentStatus

    document = create_random_document(
        db, user=get_bootstrap_user(db), status=DocumentStatus("ready")
    )
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "ready"


def test_read_document_with_failed_status(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a document with failed status."""
    from app.models import Document, DocumentStatus

    document = create_random_document(
        db, user=get_bootstrap_user(db), status=DocumentStatus("failed")
    )
    # Set processing_error for failed documents
    db_document = db.get(Document, document.id)
    if db_document:
        db_document.processing_error = "Test error message"
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "failed"


def test_read_documents_includes_status(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that reading documents list includes status field."""
    from app.models import DocumentStatus

    owner = get_bootstrap_user(db)
    create_random_document(db, user=owner, status=DocumentStatus("processing"))
    create_random_document(db, user=owner, status=DocumentStatus("ready"))
    response = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    # All documents should have status field
    for doc in content["data"]:
        assert "status" in doc
        assert doc["status"] in ["processing", "ready", "failed"]


def test_update_document_status_preserved(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that updating a document preserves its status."""
    from app.models import DocumentStatus

    document = create_random_document(
        db, user=get_bootstrap_user(db), status=DocumentStatus("ready")
    )

    data = {"filename": "updated.pdf"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["filename"] == "updated.pdf"
    assert content["status"] == "ready"  # Status should be preserved (READY)
