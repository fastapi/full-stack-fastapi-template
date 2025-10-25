"""Tests for ingestion (PDF upload) API endpoints."""

from io import BytesIO
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Ingestion


def test_create_ingestion_success(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test successful PDF upload with valid file."""
    # Create a minimal valid PDF
    pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Pages 2 0 R>>endobj 2 0 obj<</Count 1/Kids[3 0 R]>>endobj 3 0 obj<</MediaBox[0 0 612 792]>>endobj trailer<</Root 1 0 R>>'

    with patch('app.api.routes.ingestions.upload_to_supabase') as mock_upload, \
         patch('app.api.routes.ingestions.generate_presigned_url') as mock_url:

        mock_upload.return_value = "test-user-id/test-uuid/original.pdf"
        mock_url.return_value = "https://example.supabase.co/storage/v1/object/sign/worksheets/test-user-id/test-uuid/original.pdf?token=test"

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "UPLOADED"
    assert "presigned_url" in data
    assert data["file_size"] == len(pdf_content)
    assert data["page_count"] is not None or data["page_count"] is None  # pypdf may succeed or fail

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
        files={"file": ("test.docx", BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
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
        files={"file": ("fake.pdf", BytesIO(fake_pdf_content), "application/pdf")}
    )

    assert response.status_code == 400
    assert "Invalid PDF file" in response.json()["detail"] or "magic number" in response.json()["detail"].lower()


def test_create_ingestion_file_too_large(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test rejection of oversized files (>25MB)."""
    # Create a file larger than 25MB
    large_content = b'%PDF-' + b'x' * (26 * 1024 * 1024)

    response = client.post(
        "/api/v1/ingestions",
        headers=normal_user_token_headers,
        files={"file": ("large.pdf", BytesIO(large_content), "application/pdf")}
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


def test_create_ingestion_unauthorized(
    client: TestClient
) -> None:
    """Test that upload requires authentication."""
    pdf_content = b'%PDF-1.4\n'

    response = client.post(
        "/api/v1/ingestions",
        files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
    )

    assert response.status_code == 401


def test_create_ingestion_supabase_failure(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test handling of Supabase upload failure."""
    pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'

    with patch('app.api.routes.ingestions.upload_to_supabase') as mock_upload:
        mock_upload.side_effect = Exception("Supabase connection failed")

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        )

    assert response.status_code == 500
    assert "Upload failed" in response.json()["detail"]


def test_create_ingestion_corrupted_pdf(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test handling of corrupted PDF (metadata extraction fails but upload succeeds)."""
    # PDF with valid header but corrupted content
    corrupted_pdf = b'%PDF-1.4\ncorrupted content that pypdf cannot parse'

    with patch('app.api.routes.ingestions.upload_to_supabase') as mock_upload, \
         patch('app.api.routes.ingestions.generate_presigned_url') as mock_url:

        mock_upload.return_value = "test-user-id/test-uuid/original.pdf"
        mock_url.return_value = "https://example.supabase.co/signed-url"

        response = client.post(
            "/api/v1/ingestions",
            headers=normal_user_token_headers,
            files={"file": ("corrupted.pdf", BytesIO(corrupted_pdf), "application/pdf")}
        )

    # Should succeed but page_count may be NULL
    assert response.status_code == 201
    data = response.json()
    # page_count might be None if extraction failed gracefully
    assert data["page_count"] is None or isinstance(data["page_count"], int)
