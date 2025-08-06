import os
import tempfile
import uuid

import boto3
from fastapi import UploadFile

from app.core.config import settings
import textract

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def upload_file_to_s3(file: UploadFile, user_id: str) -> str:
    safe_filename = file.filename or ""
    extension = safe_filename.split(".")[-1] if "." in safe_filename else ""
    bucket = settings.S3_BUCKET_NAME
    key = f"documents/{user_id}/{uuid.uuid4()}.{extension}"

    try:
        s3.upload_fileobj(file.file, bucket, key)
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")

    return key


def generate_s3_url(key: str) -> str:
    return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{key}"

def extract_text_from_s3_file(bucket: str, key: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        s3.download_fileobj(bucket, key, tmp_file)
        tmp_path = tmp_file.name

    text = textract.process(tmp_path).decode("utf-8") or ""
    os.remove(tmp_path)
    return text