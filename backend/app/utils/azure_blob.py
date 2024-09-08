from datetime import datetime, timedelta
import secrets
from uuid import UUID
from azure.storage.blob import generate_blob_sas, BlobSasPermissions


from app.core.config import settings


async def generate_azure_presigned_url(blob_name: str, permission: BlobSasPermissions, expiry_duration: int = 1):
    """
    Generate a presigned URL for Azure Blob Storage.
    
    Args:
    - blob_name (str): The name of the blob.
    - permission (BlobSasPermissions): The permissions to grant (read, write, etc.).
    - expiry_duration (int): Duration in hours for which the URL will remain valid.

    Returns:
    - str: A presigned URL for accessing the blob.
    """
    sas_token = await generate_blob_sas(
        account_name=settings.AZURE_BLOB_STORAGE_ACCOUNT_NAME,
        container_name=settings.AZURE_BLOB_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=settings.AZURE_BLOB_ACCOUNT_KEY,
        permission=permission,
        expiry=datetime.utcnow() + timedelta(minutes=expiry_duration)
    )
    presigned_url = f"https://{settings.AZURE_BLOB_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_BLOB_CONTAINER_NAME}/{blob_name}?{sas_token}"
    return presigned_url

def generate_blob_name(user_id: UUID) -> str:
    """
    Generate a unique blob name for a user resume.
    """
    token = secrets.token_urlsafe(8)
    return f"{user_id}_{token}_{datetime.utcnow()}.pdf"