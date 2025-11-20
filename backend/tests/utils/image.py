import io
import uuid
from typing import Any

from PIL import Image as PILImage
from fastapi import UploadFile
from sqlmodel import Session

from app import crud_image as crud
from app.models import Image, ImageCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_image(db: Session) -> Image:
    """Create a random image record for testing."""
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None

    image_in = ImageCreate(
        filename=random_lower_string() + ".jpg",
        original_filename=random_lower_string() + ".jpg",
        content_type="image/jpeg",
        file_size=1024 * 100,  # 100KB
        width=800,
        height=600,
        s3_bucket="test-bucket",
        s3_key=f"images/{uuid.uuid4()}.jpg",
        s3_url=f"https://test-bucket.s3.amazonaws.com/images/{uuid.uuid4()}.jpg",
        processing_status="completed",
        alt_text=random_lower_string(),
        description=random_lower_string(),
        tags=random_lower_string()
    )
    return crud.create_image(session=db, image_in=image_in, owner_id=owner_id)


def create_test_image_upload_file(
    filename: str = "test.jpg",
    content_type: str = "image/jpeg",
    size: tuple[int, int] = (400, 300),
    format: str = "JPEG"
) -> UploadFile:
    """Create a test UploadFile with image content."""
    # Create a test image
    img = PILImage.new('RGB', size, color='red')
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)

    # Create UploadFile with new API
    upload_file = UploadFile(
        filename=filename,
        file=buffer,
        headers={"content-type": content_type}
    )
    return upload_file


def create_test_image_bytes(
    size: tuple[int, int] = (400, 300),
    format: str = "JPEG",
    color: str = "blue"
) -> bytes:
    """Create test image bytes for testing."""
    img = PILImage.new('RGB', size, color=color)
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def create_multiple_random_images(db: Session, count: int = 3) -> list[Image]:
    """Create multiple random image records for testing."""
    images = []
    for _ in range(count):
        images.append(create_random_image(db))
    return images


def create_image_with_variants(db: Session) -> Image:
    """Create an image record with test variants."""
    image = create_random_image(db)

    # Add some test variants
    from app.models import ImageVariant
    variants_data = [
        {
            "variant_type": "large",
            "width": 1200,
            "height": 900,
            "file_size": 50000,
            "s3_bucket": "test-bucket",
            "s3_key": f"variants/large/{uuid.uuid4()}.jpg",
            "s3_url": f"https://test-bucket.s3.amazonaws.com/variants/large/{uuid.uuid4()}.jpg",
            "quality": 85,
            "format": "jpeg",
            "image_id": image.id
        },
        {
            "variant_type": "medium",
            "width": 800,
            "height": 600,
            "file_size": 30000,
            "s3_bucket": "test-bucket",
            "s3_key": f"variants/medium/{uuid.uuid4()}.jpg",
            "s3_url": f"https://test-bucket.s3.amazonaws.com/variants/medium/{uuid.uuid4()}.jpg",
            "quality": 85,
            "format": "jpeg",
            "image_id": image.id
        },
        {
            "variant_type": "thumb",
            "width": 300,
            "height": 225,
            "file_size": 10000,
            "s3_bucket": "test-bucket",
            "s3_key": f"variants/thumb/{uuid.uuid4()}.jpg",
            "s3_url": f"https://test-bucket.s3.amazonaws.com/variants/thumb/{uuid.uuid4()}.jpg",
            "quality": 75,
            "format": "jpeg",
            "image_id": image.id
        }
    ]

    crud.create_image_variants(session=db, variants_data=variants_data)
    return image


def get_image_upload_data() -> dict[str, Any]:
    """Get sample image upload form data."""
    return {
        "alt_text": "Test image description",
        "description": "This is a test image for testing purposes",
        "tags": "test,upload,sample"
    }


def assert_image_response(response_data: dict[str, Any], expected_data: dict[str, Any] = None) -> None:
    """Assert that image response contains required fields."""
    required_fields = [
        "id", "filename", "original_filename", "content_type", "file_size",
        "s3_bucket", "s3_key", "s3_url", "processing_status", "owner_id"
    ]

    for field in required_fields:
        assert field in response_data, f"Missing field: {field}"

    if expected_data:
        for key, value in expected_data.items():
            assert response_data.get(key) == value, f"Field {key} mismatch: expected {value}, got {response_data.get(key)}"


def assert_variant_response(response_data: dict[str, Any]) -> None:
    """Assert that image variant response contains required fields."""
    required_fields = [
        "id", "variant_type", "width", "height", "file_size",
        "s3_bucket", "s3_key", "s3_url", "quality", "format", "image_id"
    ]

    for field in required_fields:
        assert field in response_data, f"Missing field: {field}"