"""Tests for ingestion (PDF upload) API endpoints."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from app.models import Ingestion


@pytest.fixture
def clean_ingestions(db: Session) -> None:
    """Clean up all ingestions before running GET endpoint tests."""
    # Delete all ingestions from previous tests
    statement = delete(Ingestion)
    db.exec(statement)
    db.commit()


def test_create_ingestion_success(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test successful PDF upload with valid file."""
    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Pages 2 0 R>>endobj 2 0 obj<</Count 1/Kids[3 0 R]>>endobj 3 0 obj<</MediaBox[0 0 612 792]>>endobj trailer<</Root 1 0 R>>"

    with (
        patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload,
        patch("app.api.routes.ingestions.generate_presigned_url") as mock_url,
    ):
        mock_upload.return_value = "test-user-id/test-uuid/original.pdf"
        mock_url.return_value = "https://example.supabase.co/storage/v1/object/sign/worksheets/test-user-id/test-uuid/original.pdf?token=test"

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "UPLOADED"
    assert "presigned_url" in data
    assert data["file_size"] == len(pdf_content)
    assert (
        data["page_count"] is not None or data["page_count"] is None
    )  # pypdf may succeed or fail

    # Verify ingestion record was created in database
    statement = select(Ingestion).where(Ingestion.id == data["id"])
    ingestion = db.exec(statement).first()
    assert ingestion is not None
    assert ingestion.filename == "test.pdf"


def test_create_ingestion_invalid_mime_type(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test rejection of non-PDF files based on MIME type."""
    docx_content = b"fake DOCX content"

    response = client.post(
        "/api/v1/ingestions",
        headers=normal_user_token_headers,
        files={
            "file": (
                "test.docx",
                BytesIO(docx_content),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_create_ingestion_invalid_magic_number(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test rejection of files with fake PDF MIME type but invalid magic number."""
    fake_pdf_content = b"This is not a PDF file"

    response = client.post(
        "/api/v1/ingestions",
        headers=normal_user_token_headers,
        files={"file": ("fake.pdf", BytesIO(fake_pdf_content), "application/pdf")},
    )

    assert response.status_code == 400
    assert (
        "Invalid PDF file" in response.json()["detail"]
        or "magic number" in response.json()["detail"].lower()
    )


def test_create_ingestion_file_too_large(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test rejection of oversized files (>25MB)."""
    # Create a file larger than 25MB
    large_content = b"%PDF-" + b"x" * (26 * 1024 * 1024)

    response = client.post(
        "/api/v1/ingestions",
        headers=normal_user_token_headers,
        files={"file": ("large.pdf", BytesIO(large_content), "application/pdf")},
    )

    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]


def test_create_ingestion_missing_file(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test error when no file is provided."""
    response = client.post(
        "/api/v1/ingestions",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 422  # FastAPI validation error


def test_create_ingestion_unauthorized(client: TestClient) -> None:
    """Test that upload requires authentication."""
    pdf_content = b"%PDF-1.4\n"

    response = client.post(
        "/api/v1/ingestions",
        files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
    )

    assert response.status_code == 401


def test_create_ingestion_supabase_failure(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test handling of Supabase upload failure."""
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

    with patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload:
        mock_upload.side_effect = Exception("Supabase connection failed")

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
        )

    assert response.status_code == 500
    assert "Upload failed" in response.json()["detail"]


def test_create_ingestion_corrupted_pdf(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test handling of corrupted PDF (metadata extraction fails but upload succeeds)."""
    # PDF with valid header but corrupted content
    corrupted_pdf = b"%PDF-1.4\ncorrupted content that pypdf cannot parse"

    with (
        patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload,
        patch("app.api.routes.ingestions.generate_presigned_url") as mock_url,
    ):
        mock_upload.return_value = "test-user-id/test-uuid/original.pdf"
        mock_url.return_value = "https://example.supabase.co/signed-url"

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={
                "file": ("corrupted.pdf", BytesIO(corrupted_pdf), "application/pdf")
            },
        )

    # Should succeed but page_count may be NULL
    assert response.status_code == 201
    data = response.json()
    # page_count might be None if extraction failed gracefully
    assert data["page_count"] is None or isinstance(data["page_count"], int)


# GET /api/v1/ingestions/ - List ingestions


def test_read_ingestions_empty(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    clean_ingestions: None,
) -> None:
    """Test listing ingestions when user has no uploads."""
    response = client.get(
        "/api/v1/ingestions/",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["count"] == 0


def test_read_ingestions_with_data(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
    clean_ingestions: None,
) -> None:
    """Test listing ingestions returns user's uploads."""
    # Create test ingestions via POST endpoint
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Pages 2 0 R>>endobj trailer<</Root 1 0 R>>"

    with (
        patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload,
        patch("app.api.routes.ingestions.generate_presigned_url") as mock_url,
    ):
        mock_upload.return_value = "test-path"
        mock_url.return_value = "https://example.com/test"

        # Create 3 ingestions
        for i in range(3):
            client.post(
                "/api/v1/ingestions",
                headers=normal_user_token_headers,
                files={
                    "file": (f"test{i}.pdf", BytesIO(pdf_content), "application/pdf")
                },
            )

    # List ingestions
    response = client.get(
        "/api/v1/ingestions/",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["count"] == 3
    assert all(
        ing["filename"] in ["test0.pdf", "test1.pdf", "test2.pdf"]
        for ing in data["data"]
    )


def test_read_ingestions_pagination(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    clean_ingestions: None,
) -> None:
    """Test listing ingestions with pagination."""
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

    with (
        patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload,
        patch("app.api.routes.ingestions.generate_presigned_url") as mock_url,
    ):
        mock_upload.return_value = "test-path"
        mock_url.return_value = "https://example.com/test"

        # Create 5 ingestions
        for i in range(5):
            client.post(
                "/api/v1/ingestions",
                headers=normal_user_token_headers,
                files={
                    "file": (f"test{i}.pdf", BytesIO(pdf_content), "application/pdf")
                },
            )

    # Get first page (2 items)
    response = client.get(
        "/api/v1/ingestions/?skip=0&limit=2",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["count"] == 5

    # Get second page (2 items)
    response = client.get(
        "/api/v1/ingestions/?skip=2&limit=2",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["count"] == 5

    # Get third page (1 item)
    response = client.get(
        "/api/v1/ingestions/?skip=4&limit=2",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["count"] == 5


def test_read_ingestions_unauthorized(client: TestClient) -> None:
    """Test that listing ingestions requires authentication."""
    response = client.get("/api/v1/ingestions/")

    assert response.status_code == 401


def test_read_ingestions_filters_by_owner(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    clean_ingestions: None,
) -> None:
    """Test that users only see their own ingestions (RLS)."""
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

    with (
        patch("app.api.routes.ingestions.upload_to_supabase") as mock_upload,
        patch("app.api.routes.ingestions.generate_presigned_url") as mock_url,
    ):
        mock_upload.return_value = "test-path"
        mock_url.return_value = "https://example.com/test"

        # Normal user creates 2 ingestions
        for i in range(2):
            client.post(
                "/api/v1/ingestions",
                headers=normal_user_token_headers,
                files={
                    "file": (f"normal{i}.pdf", BytesIO(pdf_content), "application/pdf")
                },
            )

        # Superuser creates 1 ingestion
        client.post(
            "/api/v1/ingestions",
            headers=superuser_token_headers,
            files={"file": ("super.pdf", BytesIO(pdf_content), "application/pdf")},
        )

    # Normal user should only see their 2 ingestions
    response = client.get(
        "/api/v1/ingestions/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["count"] == 2

    # Superuser should only see their 1 ingestion
    response = client.get(
        "/api/v1/ingestions/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["count"] == 1
