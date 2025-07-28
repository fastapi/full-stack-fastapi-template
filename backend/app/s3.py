import boto3
import uuid
from fastapi import UploadFile
from app.core.config import settings

s3 = boto3.client("s3")

def upload_file_to_s3(file: UploadFile, user_id: str) -> str:
    extension = file.filename.split(".")[-1]
    bucket = settings.S3_BUCKET_NAME
    key = f"documents/{user_id}/{uuid.uuid4()}.{extension}"

    try:
        s3.upload_fileobj(file.file, bucket, key)
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")

    return key


def generate_s3_url(key: str) -> str:
    return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{key}"