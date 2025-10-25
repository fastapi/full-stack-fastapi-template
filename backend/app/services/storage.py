"""Supabase Storage service for file upload and management."""

import logging
import re

from supabase import Client, create_client
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)


# Custom Exceptions
class StorageException(Exception):
    """Exception raised for Supabase Storage errors."""

    pass


class AuthException(Exception):
    """Exception raised for authentication/authorization errors."""

    pass


class TimeoutException(Exception):
    """Exception raised for operation timeout errors."""

    pass


def validate_storage_path(path: str) -> bool:
    """
    Validate storage path for security and format correctness.

    Args:
        path: Storage path to validate

    Returns:
        True if path is valid

    Raises:
        ValueError: If path contains security issues or invalid format
    """
    if not path or path.strip() == "":
        raise ValueError("Storage path cannot be empty")

    # Reject absolute paths
    if path.startswith("/"):
        raise ValueError(
            "Invalid storage path: absolute paths not allowed. Use relative paths."
        )

    # Reject path traversal attempts
    if ".." in path:
        raise ValueError(
            "Invalid storage path: path traversal (..) not allowed for security"
        )

    # Validate format: Should be user_id/extraction_id/filename.ext
    # Allow alphanumeric, hyphens, underscores, dots, forward slashes
    pattern = r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+$"
    if not re.match(pattern, path):
        raise ValueError(
            f"Invalid storage path format: '{path}'. Expected format: user_id/extraction_id/filename.ext"
        )

    return True


def _redact_sensitive_data(data: str, redact_after: int = 10) -> str:
    """
    Redact sensitive data for logging (service keys, tokens, etc.).

    Args:
        data: String to redact
        redact_after: Number of characters to show before redacting

    Returns:
        Redacted string
    """
    if len(data) <= redact_after:
        return "***"
    return f"{data[:redact_after]}***"


def get_supabase_client() -> Client:
    """Get Supabase client with service role key for backend operations."""
    try:
        client = create_client(
            str(settings.SUPABASE_URL), settings.SUPABASE_SERVICE_KEY
        )
        logger.debug(
            "Supabase client initialized successfully for URL: %s",
            _redact_sensitive_data(str(settings.SUPABASE_URL)),
        )
        return client
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", str(e))
        raise AuthException(f"Invalid Supabase credentials: {str(e)}") from e


@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def upload_to_supabase(
    file_path: str, file_bytes: bytes, content_type: str = "application/pdf"
) -> str:
    """
    Upload file to Supabase Storage with retry logic and path validation.

    Args:
        file_path: Storage path in format "user_id/extraction_id/original.pdf"
        file_bytes: File content as bytes
        content_type: MIME type of the file

    Returns:
        Storage path of uploaded file

    Raises:
        ValueError: If storage path is invalid or contains security issues
        StorageException: If upload fails after retry attempts
        TimeoutException: If upload exceeds timeout threshold
    """
    # Validate storage path before attempting upload
    validate_storage_path(file_path)

    file_size_mb = len(file_bytes) / (1024 * 1024)
    logger.info(
        "Starting upload to Supabase Storage: path=%s, size=%.2f MB, content_type=%s",
        file_path,
        file_size_mb,
        content_type,
    )

    try:
        supabase = get_supabase_client()

        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type},
        )

        logger.info("Upload successful: path=%s, size=%.2f MB", file_path, file_size_mb)
        return file_path

    except Exception as e:
        error_msg = str(e)
        logger.error(
            "Upload failed: path=%s, error=%s",
            file_path,
            error_msg,
        )

        # Map to specific exceptions for better error handling
        if "bucket" in error_msg.lower() and "not found" in error_msg.lower():
            raise StorageException(
                f"Bucket '{settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS}' not found. Check Supabase configuration."
            ) from e
        elif "timeout" in error_msg.lower():
            raise TimeoutException(f"Upload timed out after 30s: {error_msg}") from e
        elif "credential" in error_msg.lower() or "auth" in error_msg.lower():
            raise AuthException(f"Invalid Supabase credentials: {error_msg}") from e
        else:
            raise StorageException(
                f"Supabase Storage upload failed: {error_msg}"
            ) from e


def generate_presigned_url(
    storage_path: str,
    expiry_seconds: int = 604800,  # 7 days
) -> str:
    """
    Generate presigned URL for accessing uploaded file.

    Args:
        storage_path: Storage path in Supabase
        expiry_seconds: URL expiry time in seconds (default: 7 days, 0 for permanent)

    Returns:
        Presigned URL with expiration

    Raises:
        StorageException: If file not found or URL generation fails
    """
    logger.info(
        "Generating presigned URL: path=%s, expiry=%d seconds",
        storage_path,
        expiry_seconds,
    )

    try:
        supabase = get_supabase_client()

        response = supabase.storage.from_(
            settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS
        ).create_signed_url(path=storage_path, expires_in=expiry_seconds)

        signed_url: str = response["signedURL"]

        # Redact token from URL for logging
        url_for_logging = (
            signed_url.split("?")[0] + "?token=***" if "?" in signed_url else signed_url
        )
        logger.info(
            "Presigned URL generated successfully: path=%s, url=%s",
            storage_path,
            url_for_logging,
        )

        return signed_url

    except Exception as e:
        error_msg = str(e)
        logger.error(
            "Failed to generate presigned URL: path=%s, error=%s",
            storage_path,
            error_msg,
        )

        if "not found" in error_msg.lower():
            raise StorageException(f"File not found at path: {storage_path}") from e
        else:
            raise StorageException(
                f"Failed to generate presigned URL: {error_msg}"
            ) from e
