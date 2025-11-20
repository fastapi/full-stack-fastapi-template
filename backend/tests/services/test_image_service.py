import io
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import UploadFile
from PIL import Image

from app.services.image_service import ImageProcessingService
from app.core.config import settings
from tests.utils.image import create_test_image_upload_file, create_test_image_bytes


class TestImageProcessingService:
    """Test suite for ImageProcessingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ImageProcessingService()

    @pytest.mark.asyncio
    async def test_validate_upload_file_success(self):
        """Test successful file validation."""
        # Create a valid test image file
        upload_file = create_test_image_upload_file("test.jpg", "image/jpeg")

        result = await self.service.validate_upload_file(upload_file)
        print(f"DEBUG: Result: {result}")

        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert result['file_info']['filename'] == "test.jpg"
        assert result['file_info']['content_type'] == "image/jpeg"
        assert result['file_info']['extension'] == "jpg"

    @pytest.mark.asyncio
    async def test_validate_upload_file_no_filename(self):
        """Test file validation with no filename."""
        upload_file = UploadFile(filename=None, file=io.BytesIO(b"test"), headers={"content-type": "image/jpeg"})

        result = await self.service.validate_upload_file(upload_file)

        assert result['is_valid'] is False
        assert "No filename provided" in result['errors']

    @pytest.mark.asyncio
    async def test_validate_upload_file_invalid_extension(self):
        """Test file validation with invalid extension."""
        upload_file = create_test_image_upload_file("test.txt", "image/jpeg")

        result = await self.service.validate_upload_file(upload_file)

        assert result['is_valid'] is False
        assert "File extension '.txt' not allowed" in result['errors'][0]

    @pytest.mark.asyncio
    async def test_validate_upload_file_invalid_content_type(self):
        """Test file validation with invalid content type."""
        upload_file = create_test_image_upload_file("test.jpg", "application/pdf")

        result = await self.service.validate_upload_file(upload_file)

        assert result['is_valid'] is False
        assert "Content type 'application/pdf' not allowed" in result['errors'][0]

    @pytest.mark.asyncio
    async def test_validate_upload_file_too_large(self):
        """Test file validation with oversized file."""
        upload_file = create_test_image_upload_file()

        # Mock the file size to be too large
        # Mock the file size to be too large
        with patch.object(upload_file.file, 'tell', return_value=settings.MAX_FILE_SIZE + 1):
            result = await self.service.validate_upload_file(upload_file)

        assert result['is_valid'] is False
        assert f"File size {settings.MAX_FILE_SIZE + 1} exceeds maximum" in result['errors'][0]

    @pytest.mark.asyncio
    async def test_get_image_dimensions_success(self):
        """Test successful image dimension retrieval."""
        upload_file = create_test_image_upload_file(size=(400, 300))

        width, height = await self.service.get_image_dimensions(upload_file)

        assert width == 400
        assert height == 300

    @pytest.mark.asyncio
    async def test_get_image_dimensions_invalid_image(self):
        """Test dimension retrieval with invalid image data."""
        # Create a file with invalid image data
        invalid_file = UploadFile(
            filename="test.jpg",
            file=io.BytesIO(b"not an image"),
            headers={"content-type": "image/jpeg"}
        )

        with pytest.raises(Exception) as exc_info:
            await self.service.get_image_dimensions(invalid_file)

        assert "File is not a valid image or is corrupted" in str(exc_info.value)

    def test_get_variant_configurations(self):
        """Test variant configuration generation."""
        configs = self.service.get_variant_configurations()

        assert len(configs) == 3

        # Check large variant
        large_config = next((c for c in configs if c['type'] == 'large'), None)
        assert large_config is not None
        assert large_config['size'] == (settings.IMAGE_VARIANT_LARGE_SIZE, settings.IMAGE_VARIANT_LARGE_SIZE)
        assert large_config['quality'] == settings.IMAGE_QUALITY_LARGE
        assert large_config['format'] == 'jpeg'

        # Check medium variant
        medium_config = next((c for c in configs if c['type'] == 'medium'), None)
        assert medium_config is not None
        assert medium_config['size'] == (settings.IMAGE_VARIANT_MEDIUM_SIZE, settings.IMAGE_VARIANT_MEDIUM_SIZE)
        assert medium_config['quality'] == settings.IMAGE_QUALITY_MEDIUM

        # Check thumb variant
        thumb_config = next((c for c in configs if c['type'] == 'thumb'), None)
        assert thumb_config is not None
        assert thumb_config['size'] == (settings.IMAGE_VARIANT_THUMB_SIZE, settings.IMAGE_VARIANT_THUMB_SIZE)
        assert thumb_config['quality'] == settings.IMAGE_QUALITY_THUMB

    @pytest.mark.asyncio
    async def test_process_image_variants_success(self):
        """Test successful image variant processing."""
        # Create test image bytes
        image_content = create_test_image_bytes(size=(1200, 800))
        variant_configs = self.service.get_variant_configurations()

        variants = await self.service.process_image_variants(image_content, variant_configs)

        assert len(variants) == 3

        # Check each variant was created correctly
        for variant in variants:
            assert 'type' in variant
            assert 'width' in variant
            assert 'height' in variant
            assert 'file_size' in variant
            assert 'content' in variant
            assert 'format' in variant
            assert 'quality' in variant
            assert variant['file_size'] > 0
            assert len(variant['content']) > 0

        # Verify sizes are as expected (aspect ratio preserved)
        variants_by_type = {v['type']: v for v in variants}

        # Large variant should be close to original size (1200x800)
        large = variants_by_type['large']
        assert large['width'] <= 1200
        assert large['height'] <= 800

        # Medium variant should be smaller
        medium = variants_by_type['medium']
        assert medium['width'] <= settings.IMAGE_VARIANT_MEDIUM_SIZE
        assert medium['height'] <= settings.IMAGE_VARIANT_MEDIUM_SIZE

        # Thumb variant should be smallest
        thumb = variants_by_type['thumb']
        assert thumb['width'] <= settings.IMAGE_VARIANT_THUMB_SIZE
        assert thumb['height'] <= settings.IMAGE_VARIANT_THUMB_SIZE

    @pytest.mark.asyncio
    async def test_process_image_variants_invalid_image(self):
        """Test variant processing with invalid image data."""
        invalid_content = b"not an image"
        variant_configs = self.service.get_variant_configurations()

        with pytest.raises(Exception) as exc_info:
            await self.service.process_image_variants(invalid_content, variant_configs)

        assert "File is not a valid image or is corrupted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_image_variants_too_large(self):
        """Test variant processing with oversized image."""
        # Create an image that's too large
        oversized_content = create_test_image_bytes(
            size=(settings.IMAGE_MAX_DIMENSIONS[0] + 1, settings.IMAGE_MAX_DIMENSIONS[1] + 1)
        )
        variant_configs = self.service.get_variant_configurations()

        with pytest.raises(Exception) as exc_info:
            await self.service.process_image_variants(oversized_content, variant_configs)

        assert f"Image dimensions" in str(exc_info.value)
        assert f"exceed maximum allowed" in str(exc_info.value)

    def test_safe_filename(self):
        """Test safe filename generation."""
        # Test normal filename
        assert self.service.safe_filename("test.jpg") == "test.jpg"

        # Test filename with special characters
        assert self.service.safe_filename("test file@#$%.jpg") == "testfile.jpg"

        # Test filename with path
        assert self.service.safe_filename("/path/to/test.jpg") == "test.jpg"

        # Test very long filename
        long_name = "a" * 300 + ".jpg"
        safe_name = self.service.safe_filename(long_name)
        assert len(safe_name) <= 255
        assert safe_name.endswith(".jpg")

        # Test empty filename
        assert self.service.safe_filename("") == "unnamed_file"

    def test_get_file_hash(self):
        """Test file hash generation."""
        content1 = b"test content"
        content2 = b"test content"
        content3 = b"different content"

        hash1 = self.service.get_file_hash(content1)
        hash2 = self.service.get_file_hash(content2)
        hash3 = self.service.get_file_hash(content3)

        # Same content should have same hash
        assert hash1 == hash2
        # Different content should have different hash
        assert hash1 != hash3
        # Hash should be a string
        assert isinstance(hash1, str)
        # Hash should be consistent
        hash1_repeat = self.service.get_file_hash(content1)
        assert hash1 == hash1_repeat


# Integration test - test with real image operations
@pytest.mark.asyncio
async def test_end_to_end_image_processing():
    """Test the complete image processing pipeline."""
    service = ImageProcessingService()

    # 1. Create test image
    upload_file = create_test_image_upload_file("test.jpg", "image/jpeg", (800, 600))

    # 2. Validate file
    validation = await service.validate_upload_file(upload_file)
    assert validation['is_valid'] is True

    # 3. Get dimensions
    width, height = await service.get_image_dimensions(upload_file)
    assert width == 800
    assert height == 600

    # 4. Read file content
    await upload_file.seek(0)
    content = await upload_file.read()

    # 5. Process variants
    configs = service.get_variant_configurations()
    variants = await service.process_image_variants(content, configs)

    # 6. Verify variants
    assert len(variants) == 3
    variant_types = [v['type'] for v in variants]
    assert 'large' in variant_types
    assert 'medium' in variant_types
    assert 'thumb' in variant_types

    # 7. Verify progressive size reduction
    large = next(v for v in variants if v['type'] == 'large')
    medium = next(v for v in variants if v['type'] == 'medium')
    thumb = next(v for v in variants if v['type'] == 'thumb')

    # Large should be biggest, thumb should be smallest
    assert large['width'] >= medium['width'] >= thumb['width']
    assert large['height'] >= medium['height'] >= thumb['height']
    assert large['file_size'] >= medium['file_size'] >= thumb['file_size']