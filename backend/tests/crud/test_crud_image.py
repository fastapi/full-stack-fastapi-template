import uuid
import pytest
from sqlmodel import Session

from app import crud_image as crud
from app.models import Image, ImageCreate, ImageUpdate, User
from tests.utils.user import create_random_user
from tests.utils.image import create_random_image, create_multiple_random_images


class TestImageCRUD:
    """Test suite for Image CRUD operations."""

    def test_create_image(self, db: Session) -> None:
        """Test creating an image."""
        user = create_random_user(db)
        owner_id = user.id
        assert owner_id is not None

        image_in = ImageCreate(
            filename="test.jpg",
            original_filename="original_test.jpg",
            content_type="image/jpeg",
            file_size=1024,
            width=800,
            height=600,
            s3_bucket="test-bucket",
            s3_key="images/test.jpg",
            s3_url="https://test-bucket.s3.amazonaws.com/images/test.jpg",
            processing_status="pending",
            alt_text="Test image",
            description="A test image",
            tags="test,sample"
        )

        image = crud.create_image(session=db, image_in=image_in, owner_id=owner_id)

        assert image.filename == image_in.filename
        assert image.original_filename == image_in.original_filename
        assert image.content_type == image_in.content_type
        assert image.file_size == image_in.file_size
        assert image.width == image_in.width
        assert image.height == image_in.height
        assert image.s3_bucket == image_in.s3_bucket
        assert image.s3_key == image_in.s3_key
        assert image.s3_url == image_in.s3_url
        assert image.processing_status == image_in.processing_status
        assert image.alt_text == image_in.alt_text
        assert image.description == image_in.description
        assert image.tags == image_in.tags
        assert image.owner_id == owner_id
        assert image.id is not None

    def test_get_image(self, db: Session) -> None:
        """Test getting an image by ID."""
        image = create_random_image(db)
        retrieved_image = crud.get_image(session=db, image_id=image.id)

        assert retrieved_image is not None
        assert retrieved_image.id == image.id
        assert retrieved_image.filename == image.filename
        assert retrieved_image.owner_id == image.owner_id

    def test_get_image_not_found(self, db: Session) -> None:
        """Test getting a non-existent image."""
        fake_id = uuid.uuid4()
        retrieved_image = crud.get_image(session=db, image_id=fake_id)

        assert retrieved_image is None

    def test_get_image_with_owner_restriction(self, db: Session) -> None:
        """Test getting image with owner restriction."""
        image = create_random_image(db)
        other_user = create_random_user(db)

        # Should find image when owner_id matches
        found_image = crud.get_image(session=db, image_id=image.id, owner_id=image.owner_id)
        assert found_image is not None
        assert found_image.id == image.id

        # Should not find image when owner_id doesn't match
        found_image = crud.get_image(session=db, image_id=image.id, owner_id=other_user.id)
        assert found_image is None

    def test_get_images(self, db: Session) -> None:
        """Test getting images with pagination."""
        user = create_random_user(db)
        images = create_multiple_random_images(db, count=5)

        # Filter images by our user
        user_images = [img for img in images if img.owner_id == user.id]
        if not user_images:
            # Create images for this specific user
            user_images = []
            for _ in range(3):
                img = create_random_image(db)
                img.owner_id = user.id
                db.add(img)
                db.commit()
                db.refresh(img)
                user_images.append(img)

        retrieved_images, total_count = crud.get_images(
            session=db,
            owner_id=user.id,
            skip=0,
            limit=10
        )

        assert len(retrieved_images) == len(user_images)
        assert total_count == len(user_images)
        assert all(img.owner_id == user.id for img in retrieved_images)

    def test_get_images_with_pagination(self, db: Session) -> None:
        """Test image pagination."""
        user = create_random_user(db)

        # Create images for this user
        created_images = []
        for _ in range(5):
            img = create_random_image(db)
            img.owner_id = user.id
            db.add(img)
            db.commit()
            db.refresh(img)
            created_images.append(img)

        # Get first page
        first_page, total_count = crud.get_images(
            session=db,
            owner_id=user.id,
            skip=0,
            limit=2
        )

        # Get second page
        second_page, _ = crud.get_images(
            session=db,
            owner_id=user.id,
            skip=2,
            limit=2
        )

        assert len(first_page) == 2
        assert len(second_page) == 2
        assert total_count >= 5  # At least our created images
        assert first_page[0].id != second_page[0].id  # Different images

    def test_get_images_with_search(self, db: Session) -> None:
        """Test image search functionality."""
        user = create_random_user(db)

        # Create image with searchable content
        image_in = ImageCreate(
            filename="searchable_test.jpg",
            original_filename="searchable_original.jpg",
            content_type="image/jpeg",
            file_size=1024,
            width=800,
            height=600,
            s3_bucket="test-bucket",
            s3_key="images/searchable_test.jpg",
            s3_url="https://test-bucket.s3.amazonaws.com/images/searchable_test.jpg",
            processing_status="completed",
            alt_text="Unique search keyword",
            description="Searchable description with special terms",
            tags="search,keyword,unique"
        )

        created_image = crud.create_image(session=db, image_in=image_in, owner_id=user.id)

        # Search by alt_text
        found_images, total_count = crud.get_images(
            session=db,
            owner_id=user.id,
            search="Unique search"
        )

        assert len(found_images) == 1
        assert found_images[0].id == created_image.id

        # Search by tags
        found_images, total_count = crud.get_images(
            session=db,
            owner_id=user.id,
            search="search,keyword"
        )

        assert len(found_images) == 1
        assert found_images[0].id == created_image.id

    def test_get_images_with_processing_status_filter(self, db: Session) -> None:
        """Test filtering images by processing status."""
        user = create_random_user(db)

        # Create images with different processing statuses
        completed_image = create_random_image(db)
        completed_image.processing_status = "completed"

        pending_image = create_random_image(db)
        pending_image.processing_status = "pending"

        # Filter by completed status
        completed_images, _ = crud.get_images(
            session=db,
            owner_id=user.id,
            processing_status="completed"
        )

        assert all(img.processing_status == "completed" for img in completed_images)

    def test_update_image(self, db: Session) -> None:
        """Test updating image metadata."""
        image = create_random_image(db)

        update_data = ImageUpdate(
            alt_text="Updated alt text",
            description="Updated description",
            tags="updated,new,tag"
        )

        updated_image = crud.update_image(
            session=db,
            db_image=image,
            image_in=update_data
        )

        assert updated_image.alt_text == "Updated alt text"
        assert updated_image.description == "Updated description"
        assert updated_image.tags == "updated,new,tag"
        # Other fields should remain unchanged
        assert updated_image.filename == image.filename
        assert updated_image.file_size == image.file_size

    def test_update_image_partial(self, db: Session) -> None:
        """Test partial image update."""
        image = create_random_image(db)
        original_description = image.description

        update_data = ImageUpdate(alt_text="Only update alt text")

        updated_image = crud.update_image(
            session=db,
            db_image=image,
            image_in=update_data
        )

        assert updated_image.alt_text == "Only update alt text"
        assert updated_image.description == original_description  # Should remain unchanged

    def test_delete_image(self, db: Session) -> None:
        """Test deleting an image."""
        image = create_random_image(db)
        image_id = image.id

        deleted_image = crud.delete_image(
            session=db,
            image_id=image_id,
            owner_id=image.owner_id
        )

        assert deleted_image is not None
        assert deleted_image.id == image_id

        # Verify image is deleted
        retrieved_image = crud.get_image(session=db, image_id=image_id)
        assert retrieved_image is None

    def test_delete_image_not_found(self, db: Session) -> None:
        """Test deleting a non-existent image."""
        user = create_random_user(db)
        fake_id = uuid.uuid4()

        deleted_image = crud.delete_image(
            session=db,
            image_id=fake_id,
            owner_id=user.id
        )

        assert deleted_image is None

    def test_delete_image_wrong_owner(self, db: Session) -> None:
        """Test deleting image with wrong owner."""
        image = create_random_image(db)
        other_user = create_random_user(db)

        deleted_image = crud.delete_image(
            session=db,
            image_id=image.id,
            owner_id=other_user.id
        )

        assert deleted_image is None

    def test_create_processing_job(self, db: Session) -> None:
        """Test creating a processing job."""
        image = create_random_image(db)

        processing_job = crud.create_processing_job(
            session=db,
            image_id=image.id
        )

        assert processing_job is not None
        assert processing_job.image_id == image.id
        assert processing_job.status == "pending"
        assert processing_job.retry_count == 0
        assert processing_job.id is not None

    def test_get_processing_job(self, db: Session) -> None:
        """Test getting a processing job."""
        image = create_random_image(db)
        created_job = crud.create_processing_job(session=db, image_id=image.id)

        retrieved_job = crud.get_processing_job(session=db, image_id=image.id)

        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.image_id == image.id

    def test_update_processing_job(self, db: Session) -> None:
        """Test updating a processing job."""
        image = create_random_image(db)
        processing_job = crud.create_processing_job(session=db, image_id=image.id)

        updated_job = crud.update_processing_job(
            session=db,
            job_id=processing_job.id,
            status="completed",
            error_message=None
        )

        assert updated_job is not None
        assert updated_job.status == "completed"
        assert updated_job.error_message is None

    def test_update_processing_job_with_error(self, db: Session) -> None:
        """Test updating processing job with error."""
        image = create_random_image(db)
        processing_job = crud.create_processing_job(session=db, image_id=image.id)

        error_message = "Processing failed due to network error"
        updated_job = crud.update_processing_job(
            session=db,
            job_id=processing_job.id,
            status="failed",
            error_message=error_message
        )

        assert updated_job is not None
        assert updated_job.status == "failed"
        assert updated_job.error_message == error_message

    def test_get_user_image_stats(self, db: Session) -> None:
        """Test getting user image statistics."""
        user = create_random_user(db)

        # Create some images for the user
        created_images = []
        for _ in range(3):
            img = create_random_image(db)
            # Update to belong to our test user
            img.owner_id = user.id
            db.add(img)
            created_images.append(img)

        db.commit()

        stats = crud.get_user_image_stats(session=db, owner_id=user.id)

        assert "total_images" in stats
        assert "total_file_size" in stats
        assert "processing_status_counts" in stats
        assert "average_file_size" in stats
        assert stats["total_images"] >= 3
        assert stats["total_file_size"] > 0
        assert stats["average_file_size"] > 0

    def test_search_images_globally(self, db: Session) -> None:
        """Test global image search functionality."""
        # Create images with unique content for searching
        image_in1 = ImageCreate(
            filename="global_search_test1.jpg",
            original_filename="global_original1.jpg",
            content_type="image/jpeg",
            file_size=1024,
            width=800,
            height=600,
            s3_bucket="test-bucket",
            s3_key="images/global_test1.jpg",
            s3_url="https://test-bucket.s3.amazonaws.com/images/global_test1.jpg",
            processing_status="completed",
            alt_text="Global unique keyword for search",
            description="Global search test description",
            tags="global,search,unique"
        )

        image_in2 = ImageCreate(
            filename="global_search_test2.jpg",
            original_filename="global_original2.jpg",
            content_type="image/jpeg",
            file_size=2048,
            width=1200,
            height=900,
            s3_bucket="test-bucket",
            s3_key="images/global_test2.jpg",
            s3_url="https://test-bucket.s3.amazonaws.com/images/global_test2.jpg",
            processing_status="completed",
            alt_text="Another global unique term",
            description="Different searchable content",
            tags="another,global,term"
        )

        user1 = create_random_user(db)
        user2 = create_random_user(db)

        image1 = crud.create_image(session=db, image_in=image_in1, owner_id=user1.id)
        image2 = crud.create_image(session=db, image_in=image_in2, owner_id=user2.id)

        # Search globally
        found_images, total_count = crud.search_images_globally(
            session=db,
            query="global unique"
        )

        assert len(found_images) >= 1
        assert total_count >= 1

        # Search by specific user
        found_images, _ = crud.search_images_globally(
            session=db,
            query="global unique",
            owner_id=user1.id
        )

        assert len(found_images) >= 1
        assert all(img.owner_id == user1.id for img in found_images)