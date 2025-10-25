"""Unit tests for Supabase Storage service."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.storage import (
    StorageException,
    generate_presigned_url,
    get_supabase_client,
    upload_to_supabase,
    validate_storage_path,
)


class TestGetSupabaseClient:
    """Test Supabase client initialization."""

    @patch("app.services.storage.create_client")
    def test_get_supabase_client_success(self, mock_create_client):
        """Test successful Supabase client creation with service key."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_URL = "https://test.supabase.co"
            mock_settings.SUPABASE_SERVICE_KEY = "test-service-key"

            client = get_supabase_client()

            # Verify create_client called with correct parameters
            mock_create_client.assert_called_once_with(
                "https://test.supabase.co", "test-service-key"
            )
            assert client == mock_client

    @patch("app.services.storage.create_client")
    def test_get_supabase_client_invalid_credentials(self, mock_create_client):
        """Test client creation with invalid credentials raises exception."""
        mock_create_client.side_effect = Exception("Invalid API key")

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_URL = "https://test.supabase.co"
            mock_settings.SUPABASE_SERVICE_KEY = "invalid-key"

            with pytest.raises(Exception) as exc_info:
                get_supabase_client()

            assert "Invalid API key" in str(exc_info.value)


class TestValidateStoragePath:
    """Test storage path validation."""

    def test_validate_storage_path_valid_uuid_format(self):
        """Test valid UUID-based storage path passes validation."""
        valid_paths = [
            "550e8400-e29b-41d4-a716-446655440000/7c9e6679-7425-40de-944b-e07fc1f90ae7/original.pdf",
            "user-123/extract-456/file.pdf",
            "a1b2c3d4/e5f6g7h8/document.pdf",
        ]

        for path in valid_paths:
            # Should not raise exception
            validate_storage_path(path)

    def test_validate_storage_path_rejects_path_traversal(self):
        """Test path validation rejects path traversal attempts."""
        invalid_paths = [
            "../../../etc/passwd",
            "user/../admin/file.pdf",
            "user/extract/../../../secret.pdf",
            "user/extract/../../file.pdf",
        ]

        for path in invalid_paths:
            with pytest.raises(ValueError) as exc_info:
                validate_storage_path(path)
            assert "path traversal" in str(exc_info.value).lower()

    def test_validate_storage_path_rejects_absolute_paths(self):
        """Test path validation rejects absolute paths."""
        invalid_paths = [
            "/etc/passwd",
            "/var/www/upload.pdf",
            "/home/user/file.pdf",
        ]

        for path in invalid_paths:
            with pytest.raises(ValueError) as exc_info:
                validate_storage_path(path)
            assert "absolute path" in str(exc_info.value).lower()

    def test_validate_storage_path_rejects_empty_string(self):
        """Test path validation rejects empty paths."""
        with pytest.raises(ValueError) as exc_info:
            validate_storage_path("")
        assert "empty" in str(exc_info.value).lower()


class TestUploadToSupabase:
    """Test file upload to Supabase Storage."""

    @patch("app.services.storage.get_supabase_client")
    def test_upload_to_supabase_success(self, mock_get_client):
        """Test successful file upload to Supabase Storage."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_client.storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = {"path": "test-path"}
        mock_get_client.return_value = mock_client

        file_bytes = b"test file content"
        storage_path = "user-123/extract-456/test.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            result = upload_to_supabase(storage_path, file_bytes, "application/pdf")

            # Verify bucket selection
            mock_client.storage.from_.assert_called_once_with("worksheets")

            # Verify upload called with correct parameters
            mock_bucket.upload.assert_called_once_with(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf"},
            )

            assert result == storage_path

    @patch("app.services.storage.get_supabase_client")
    def test_upload_to_supabase_retries_on_transient_failure(self, mock_get_client):
        """Test upload retries on transient network failures."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        # Fail first 2 attempts, succeed on 3rd
        mock_bucket.upload.side_effect = [
            Exception("Network timeout"),
            Exception("Connection reset"),
            {"path": "test-path"},
        ]

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        file_bytes = b"test content"
        storage_path = "user-123/extract-456/test.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            result = upload_to_supabase(storage_path, file_bytes, "application/pdf")

            # Verify upload was called 3 times (2 failures + 1 success)
            assert mock_bucket.upload.call_count == 3
            assert result == storage_path

    @patch("app.services.storage.get_supabase_client")
    def test_upload_to_supabase_raises_after_max_retries(self, mock_get_client):
        """Test upload raises exception after max retry attempts."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        # Fail all 3 attempts
        mock_bucket.upload.side_effect = Exception("Persistent network failure")

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        file_bytes = b"test content"
        storage_path = "user-123/extract-456/test.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            with pytest.raises(Exception) as exc_info:
                upload_to_supabase(storage_path, file_bytes, "application/pdf")

            assert "Persistent network failure" in str(exc_info.value)
            # Verify upload was attempted 3 times
            assert mock_bucket.upload.call_count == 3

    @patch("app.services.storage.get_supabase_client")
    def test_upload_to_supabase_validates_path(self, mock_get_client):
        """Test upload validates storage path before uploading."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        file_bytes = b"test content"
        invalid_path = "../../../etc/passwd"

        with pytest.raises(ValueError) as exc_info:
            upload_to_supabase(invalid_path, file_bytes, "application/pdf")

        assert "path traversal" in str(exc_info.value).lower()

    @patch("app.services.storage.get_supabase_client")
    def test_upload_to_supabase_bucket_not_found(self, mock_get_client):
        """Test upload handles bucket not found error."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_bucket.upload.side_effect = StorageException(
            "Bucket 'worksheets' not found. Check Supabase configuration."
        )

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        file_bytes = b"test content"
        storage_path = "user-123/extract-456/test.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            with pytest.raises(StorageException) as exc_info:
                upload_to_supabase(storage_path, file_bytes, "application/pdf")

            assert "Bucket 'worksheets' not found" in str(exc_info.value)


class TestGeneratePresignedUrl:
    """Test presigned URL generation."""

    @patch("app.services.storage.get_supabase_client")
    def test_generate_presigned_url_success(self, mock_get_client):
        """Test successful presigned URL generation with default 7-day expiry."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://example.supabase.co/storage/v1/object/sign/worksheets/test-path?token=abc123"
        }

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        storage_path = "user-123/extract-456/test.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            url = generate_presigned_url(storage_path)

            # Verify bucket selection
            mock_client.storage.from_.assert_called_once_with("worksheets")

            # Verify create_signed_url called with default 7-day expiry
            mock_bucket.create_signed_url.assert_called_once_with(
                path=storage_path, expires_in=604800
            )

            assert url == "https://example.supabase.co/storage/v1/object/sign/worksheets/test-path?token=abc123"

    @patch("app.services.storage.get_supabase_client")
    def test_generate_presigned_url_custom_expiry(self, mock_get_client):
        """Test presigned URL generation with custom expiry time."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://example.supabase.co/signed-url"
        }

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        storage_path = "user-123/extract-456/test.pdf"
        custom_expiry = 3600  # 1 hour

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            generate_presigned_url(storage_path, expiry_seconds=custom_expiry)

            # Verify create_signed_url called with custom expiry
            mock_bucket.create_signed_url.assert_called_once_with(
                path=storage_path, expires_in=custom_expiry
            )

    @patch("app.services.storage.get_supabase_client")
    def test_generate_presigned_url_file_not_found(self, mock_get_client):
        """Test presigned URL generation when file doesn't exist."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_bucket.create_signed_url.side_effect = StorageException(
            "File not found at path: user-123/extract-456/nonexistent.pdf"
        )

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        storage_path = "user-123/extract-456/nonexistent.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            with pytest.raises(StorageException) as exc_info:
                generate_presigned_url(storage_path)

            assert "File not found" in str(exc_info.value)

    @patch("app.services.storage.get_supabase_client")
    def test_generate_presigned_url_permanent(self, mock_get_client):
        """Test presigned URL generation with no expiry (permanent)."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()

        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://example.supabase.co/permanent-url"
        }

        mock_client.storage.from_.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        storage_path = "user-123/extract-456/approved.pdf"

        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS = "worksheets"

            generate_presigned_url(storage_path, expiry_seconds=0)

            # Verify create_signed_url called with 0 expiry (permanent)
            mock_bucket.create_signed_url.assert_called_once_with(
                path=storage_path, expires_in=0
            )


class TestStorageExceptions:
    """Test custom storage exception classes."""

    def test_storage_exception_message(self):
        """Test StorageException can be created with custom message."""
        error_msg = "Supabase Storage unreachable"
        exc = StorageException(error_msg)

        assert str(exc) == error_msg
        assert isinstance(exc, Exception)

    def test_storage_exception_with_details(self):
        """Test StorageException with additional details."""
        error_msg = "Upload failed"
        details = "Network timeout after 30s"
        exc = StorageException(f"{error_msg}: {details}")

        assert error_msg in str(exc)
        assert details in str(exc)
