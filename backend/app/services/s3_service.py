import logging
import os
import uuid
from io import BytesIO
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException
from PIL import Image

from app.core.config import settings


class S3Service:
    """AWS S3 service for file operations."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET
        self.cloudfront_domain = settings.AWS_CLOUDFRONT_DOMAIN

    def _generate_s3_key(self, filename: str, prefix: str = "images") -> str:
        """Generate unique S3 key for file."""
        # Extract file extension
        file_ext = os.path.splitext(filename)[1].lower()
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        # Create S3 key
        return f"{prefix}/{unique_filename}"

    def _get_public_url(self, s3_key: str) -> str:
        """Get public URL for S3 object."""
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{s3_key}"

        # Construct S3 URL if CloudFront is not configured
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        prefix: str = "images"
    ) -> dict:
        """
        Upload file to S3.

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            prefix: S3 prefix for the file

        Returns:
            Dictionary with s3_key, s3_url, and file_size
        """
        try:
            s3_key = self._generate_s3_key(filename, prefix)
            file_size = len(file_content)

            # Upload file with server-side encryption
            self.s3_client.upload_fileobj(
                Fileobj=BytesIO(file_content),
                Bucket=self.bucket_name,
                Key=s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'original_filename': filename,
                        'content_type': content_type,
                    }
                }
            )

            return {
                's3_key': s3_key,
                's3_url': self._get_public_url(s3_key),
                's3_bucket': self.bucket_name,
                'file_size': file_size
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 bucket '{self.bucket_name}' does not exist"
                )
            elif error_code == 'AccessDenied':
                raise HTTPException(
                    status_code=500,
                    detail="Access denied to S3 bucket. Check permissions."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 upload failed: {str(e)}"
                )
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials not found. Check configuration."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during upload: {str(e)}"
            )

    async def upload_image_variants(
        self,
        image: Image.Image,
        original_filename: str,
        variant_types: list[dict]
    ) -> list[dict]:
        """
        Upload multiple image variants to S3.

        Args:
            image: PIL Image object
            original_filename: Original filename
            variant_types: List of variant configurations

        Returns:
            List of uploaded variant information
        """
        variants = []

        for variant_config in variant_types:
            try:
                # Create variant copy
                variant_image = image.copy()

                # Resize if needed
                if variant_config['size']:
                    variant_image.thumbnail(
                        variant_config['size'],
                        Image.Resampling.LANCZOS
                    )
                    width, height = variant_image.size
                else:
                    width, height = image.size

                # Convert to RGB if needed (for JPEG)
                if variant_config['format'] == 'jpeg' and variant_image.mode != 'RGB':
                    variant_image = variant_image.convert('RGB')

                # Save to bytes
                buffer = BytesIO()
                save_params = {
                    'format': variant_config['format'],
                    'quality': variant_config['quality'],
                    'optimize': True
                }

                if variant_config['format'] == 'jpeg':
                    save_params['progressive'] = True
                elif variant_config['format'] == 'png':
                    save_params['compress_level'] = 6

                variant_image.save(buffer, **save_params)
                buffer.seek(0)
                file_content = buffer.getvalue()

                # Generate filename for variant
                base_name = os.path.splitext(original_filename)[0]
                variant_filename = f"{base_name}_{variant_config['type']}.{variant_config['format']}"
                content_type = f"image/{variant_config['format']}"

                # Upload variant
                result = await self.upload_file(
                    file_content=file_content,
                    filename=variant_filename,
                    content_type=content_type,
                    prefix=f"variants/{variant_config['type']}"
                )

                variants.append({
                    'variant_type': variant_config['type'],
                    'width': width,
                    'height': height,
                    'file_size': result['file_size'],
                    's3_bucket': result['s3_bucket'],
                    's3_key': result['s3_key'],
                    's3_url': result['s3_url'],
                    'quality': variant_config['quality'],
                    'format': variant_config['format']
                })

            except Exception as e:
                # Log error but continue with other variants
                logger.error(f"Error creating variant {variant_config['type']}: {str(e)}")
                continue

        return variants

    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            s3_key: S3 key of the file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True

        except ClientError as e:
            logger.error(f"Error deleting file {s3_key}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file {s3_key}: {str(e)}")
            return False

    async def generate_presigned_url(
        self,
        s3_key: str,
        expires_in: int = 3600,
        method: str = 'get_object'
    ) -> Optional[str]:
        """
        Generate presigned URL for S3 object.

        Args:
            s3_key: S3 key of the object
            expires_in: URL expiration time in seconds
            method: S3 operation method

        Returns:
            Presigned URL or None if error
        """
        try:
            return self.s3_client.generate_presigned_url(
                method,
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.error(f"Error generating presigned URL for {s3_key}: {str(e)}")
            return None

    async def check_file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3.

        Args:
            s3_key: S3 key to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking file existence {s3_key}: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking file {s3_key}: {str(e)}")
            return False


# Logger instance
logger = logging.getLogger(__name__)

# Singleton instance
s3_service = S3Service()