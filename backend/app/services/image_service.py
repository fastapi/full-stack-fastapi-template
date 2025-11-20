import io
import logging
import os
from typing import Tuple, Optional

import aiofiles
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlmodel import Session

from app.core.config import settings


class ImageProcessingService:
    """Service for image validation and processing operations."""

    @staticmethod
    async def validate_upload_file(file: UploadFile) -> dict:
        """
        Validate uploaded file for image processing.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Dictionary with validation results and file info
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'file_info': {}
        }

        try:
            # Check if filename exists
            if not file.filename:
                print("DEBUG: No filename")
                validation_result['errors'].append("No filename provided")
                return validation_result

            # Check file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in [f'.{ext}' for ext in settings.ALLOWED_IMAGE_EXTENSIONS]:
                print(f"DEBUG: Bad extension {file_ext}")
                validation_result['errors'].append(
                    f"File extension '{file_ext}' not allowed. "
                    f"Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
                )
                return validation_result

            # Check MIME type
            if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                print(f"DEBUG: Bad content type {file.content_type}")
                validation_result['errors'].append(
                    f"Content type '{file.content_type}' not allowed. "
                    f"Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
                )
                return validation_result

            # Get file size
            # Get file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            await file.seek(0)  # Reset position
            print(f"DEBUG: File size {file_size}")

            if file_size > settings.MAX_FILE_SIZE:
                print(f"DEBUG: File too large {file_size}")
                validation_result['errors'].append(
                    f"File size {file_size} exceeds maximum allowed size {settings.MAX_FILE_SIZE}"
                )
                return validation_result

            # Store file info
            validation_result['file_info'] = {
                'filename': file.filename,
                'original_filename': file.filename,
                'content_type': file.content_type,
                'file_size': file_size,
                'extension': file_ext[1:]  # Remove dot
            }

            validation_result['is_valid'] = True
            return validation_result

        except Exception as e:
            print(f"DEBUG: Validation error: {str(e)}")
            validation_result['errors'].append(f"Validation error: {str(e)}")
            return validation_result

    @staticmethod
    async def get_image_dimensions(file: UploadFile) -> Tuple[int, int]:
        """
        Get image dimensions from UploadFile.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Tuple of (width, height)
        """
        try:
            # Read file content
            await file.seek(0)
            content = await file.read()
            await file.seek(0)

            # Create image from bytes
            with Image.open(io.BytesIO(content)) as img:
                return img.size  # (width, height)

        except UnidentifiedImageError:
            raise HTTPException(
                status_code=400,
                detail="File is not a valid image or is corrupted"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading image dimensions: {str(e)}"
            )

    @staticmethod
    def get_variant_configurations() -> list[dict]:
        """
        Get image variant configurations from settings.

        Returns:
            List of variant configuration dictionaries
        """
        return [
            {
                'type': 'large',
                'size': (settings.IMAGE_VARIANT_LARGE_SIZE, settings.IMAGE_VARIANT_LARGE_SIZE),
                'quality': settings.IMAGE_QUALITY_LARGE,
                'format': 'jpeg'
            },
            {
                'type': 'medium',
                'size': (settings.IMAGE_VARIANT_MEDIUM_SIZE, settings.IMAGE_VARIANT_MEDIUM_SIZE),
                'quality': settings.IMAGE_QUALITY_MEDIUM,
                'format': 'jpeg'
            },
            {
                'type': 'thumb',
                'size': (settings.IMAGE_VARIANT_THUMB_SIZE, settings.IMAGE_VARIANT_THUMB_SIZE),
                'quality': settings.IMAGE_QUALITY_THUMB,
                'format': 'jpeg'
            }
        ]

    @staticmethod
    async def process_image_variants(
        file_content: bytes,
        variant_configs: list[dict]
    ) -> list[dict]:
        """
        Process image variants from original file content.

        Args:
            file_content: Original image file content as bytes
            variant_configs: List of variant configurations

        Returns:
            List of processed variant information
        """
        variants = []

        try:
            # Load original image
            with Image.open(io.BytesIO(file_content)) as img:
                original_width, original_height = img.size

                # Check if image is too large for safe processing
                max_width, max_height = settings.IMAGE_MAX_DIMENSIONS
                if original_width > max_width or original_height > max_height:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image dimensions {original_width}x{original_height} exceed maximum allowed {max_width}x{max_height}"
                    )

                # Process each variant
                for config in variant_configs:
                    try:
                        # Create variant copy
                        variant_img = img.copy()

                        # Calculate target size while maintaining aspect ratio
                        target_size = config['size']
                        if target_size:
                            # Calculate aspect ratio
                            aspect_ratio = original_width / original_height

                            if original_width > original_height:
                                # Landscape: width is the limiting factor
                                new_width = min(target_size[0], original_width)
                                new_height = int(new_width / aspect_ratio)
                            else:
                                # Portrait: height is the limiting factor
                                new_height = min(target_size[1], original_height)
                                new_width = int(new_height * aspect_ratio)

                            # Resize with high quality
                            variant_img = variant_img.resize(
                                (new_width, new_height),
                                Image.Resampling.LANCZOS
                            )
                            final_width, final_height = new_width, new_height
                        else:
                            final_width, final_height = original_width, original_height

                        # Convert to RGB if needed (for JPEG)
                        if config['format'] == 'jpeg' and variant_img.mode != 'RGB':
                            variant_img = variant_img.convert('RGB')

                        # Save to bytes buffer
                        buffer = io.BytesIO()
                        save_params = {
                            'format': config['format'],
                            'quality': config['quality'],
                            'optimize': True
                        }

                        if config['format'] == 'jpeg':
                            save_params['progressive'] = True
                        elif config['format'] == 'png':
                            save_params['compress_level'] = 6
                        elif config['format'] == 'webp':
                            save_params['method'] = 6

                        variant_img.save(buffer, **save_params)
                        variant_content = buffer.getvalue()

                        variants.append({
                            'type': config['type'],
                            'width': final_width,
                            'height': final_height,
                            'file_size': len(variant_content),
                            'content': variant_content,
                            'format': config['format'],
                            'quality': config['quality']
                        })

                    except Exception as e:
                        logger.error(f"Error processing variant {config['type']}: {str(e)}")
                        continue

            return variants

        except UnidentifiedImageError:
            raise HTTPException(
                status_code=400,
                detail="File is not a valid image or is corrupted"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing image variants: {str(e)}"
            )

    @staticmethod
    def safe_filename(filename: str, max_length: int = 255) -> str:
        """
        Generate a safe filename by removing special characters and limiting length.

        Args:
            filename: Original filename
            max_length: Maximum allowed filename length

        Returns:
            Safe filename
        """
        # Get the basename (remove directory paths)
        safe_name = os.path.basename(filename)

        # Remove special characters except alphanumerics, dots, hyphens, and underscores
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '._-')

        # Limit length
        if len(safe_name) > max_length:
            # Preserve extension
            name, ext = os.path.splitext(safe_name)
            safe_name = f"{name[:max_length - len(ext)]}{ext}"

        return safe_name or "unnamed_file"

    @staticmethod
    def get_file_hash(file_content: bytes) -> str:
        """
        Generate hash for file content to detect duplicates.

        Args:
            file_content: File content as bytes

        Returns:
            SHA-256 hash of the file content
        """
        import hashlib

        return hashlib.sha256(file_content).hexdigest()


# Singleton instance
image_service = ImageProcessingService()