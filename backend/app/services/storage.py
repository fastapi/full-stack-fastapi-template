"""Supabase Storage service for file upload and management."""

from supabase import Client, create_client
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client with service role key for backend operations."""
    return create_client(str(settings.SUPABASE_URL), settings.SUPABASE_SERVICE_KEY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def upload_to_supabase(
    file_path: str, file_bytes: bytes, content_type: str = "application/pdf"
) -> str:
    """
    Upload file to Supabase Storage with retry logic.

    Args:
        file_path: Storage path in format "user_id/extraction_id/original.pdf"
        file_bytes: File content as bytes
        content_type: MIME type of the file

    Returns:
        Storage path of uploaded file

    Raises:
        Exception: If upload fails after 3 retry attempts
    """
    supabase = get_supabase_client()

    supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS).upload(
        path=file_path, file=file_bytes, file_options={"content-type": content_type}
    )

    return file_path


def generate_presigned_url(
    storage_path: str,
    expiry_seconds: int = 604800,  # 7 days
) -> str:
    """
    Generate presigned URL for accessing uploaded file.

    Args:
        storage_path: Storage path in Supabase
        expiry_seconds: URL expiry time in seconds (default: 7 days)

    Returns:
        Presigned URL with expiration
    """
    supabase = get_supabase_client()

    response = supabase.storage.from_(
        settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS
    ).create_signed_url(path=storage_path, expires_in=expiry_seconds)

    signed_url: str = response["signedURL"]
    return signed_url
