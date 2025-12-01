"""Unit tests for Photo CRUD operations"""

import uuid

from sqlmodel import Session

from app import crud
from app.models import (
    GalleryCreate,
    OrganizationCreate,
    PhotoCreate,
    ProjectCreate,
)


def test_create_photo(db: Session) -> None:
    """Test creating a new photo"""
    # Setup: create org, project, and gallery
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create photo
    photo_in = PhotoCreate(
        gallery_id=gallery.id,
        filename="test-photo.jpg",
        url="/api/v1/galleries/test/photos/test-photo.jpg",
        file_size=1024,
    )

    photo = crud.create_photo(session=db, photo_in=photo_in)

    assert photo.filename == "test-photo.jpg"
    assert photo.file_size == 1024
    assert photo.gallery_id == gallery.id
    assert photo.id is not None
    assert photo.uploaded_at is not None

    # Verify gallery photo_count was updated
    db.refresh(gallery)
    assert gallery.photo_count == 1


def test_get_photos_by_gallery(db: Session) -> None:
    """Test retrieving photos for a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create multiple photos
    for i in range(3):
        photo_in = PhotoCreate(
            gallery_id=gallery.id,
            filename=f"photo-{i}.jpg",
            url=f"/api/v1/galleries/{gallery.id}/photos/photo-{i}.jpg",
            file_size=1024 * (i + 1),
        )
        crud.create_photo(session=db, photo_in=photo_in)

    # Retrieve photos
    photos = crud.get_photos_by_gallery(session=db, gallery_id=gallery.id)

    assert len(photos) == 3
    filenames = [p.filename for p in photos]
    assert "photo-0.jpg" in filenames
    assert "photo-1.jpg" in filenames
    assert "photo-2.jpg" in filenames


def test_count_photos_in_gallery(db: Session) -> None:
    """Test counting photos in a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Initially should have 0 photos
    count = crud.count_photos_in_gallery(session=db, gallery_id=gallery.id)
    assert count == 0

    # Create 5 photos
    for i in range(5):
        photo_in = PhotoCreate(
            gallery_id=gallery.id,
            filename=f"photo-{i}.jpg",
            url=f"/api/v1/galleries/{gallery.id}/photos/photo-{i}.jpg",
            file_size=1024,
        )
        crud.create_photo(session=db, photo_in=photo_in)

    # Should now have 5 photos
    count = crud.count_photos_in_gallery(session=db, gallery_id=gallery.id)
    assert count == 5


def test_delete_photos(db: Session) -> None:
    """Test deleting photos from a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create photos
    photo_ids = []
    for i in range(3):
        photo_in = PhotoCreate(
            gallery_id=gallery.id,
            filename=f"photo-{i}.jpg",
            url=f"/api/v1/galleries/{gallery.id}/photos/photo-{i}.jpg",
            file_size=1024,
        )
        photo = crud.create_photo(session=db, photo_in=photo_in)
        photo_ids.append(photo.id)

    # Verify photos exist
    assert crud.count_photos_in_gallery(session=db, gallery_id=gallery.id) == 3

    # Delete 2 photos
    deleted_count = crud.delete_photos(
        session=db, gallery_id=gallery.id, photo_ids=photo_ids[:2]
    )

    assert deleted_count == 2
    assert crud.count_photos_in_gallery(session=db, gallery_id=gallery.id) == 1

    # Verify gallery photo_count was updated
    db.refresh(gallery)
    assert gallery.photo_count == 1


def test_delete_photos_empty_list(db: Session) -> None:
    """Test deleting photos with empty list"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Delete with empty list
    deleted_count = crud.delete_photos(session=db, gallery_id=gallery.id, photo_ids=[])

    assert deleted_count == 0


def test_delete_photos_nonexistent_ids(db: Session) -> None:
    """Test deleting photos with IDs that don't exist"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Try to delete non-existent photos
    fake_ids = [uuid.uuid4(), uuid.uuid4()]
    deleted_count = crud.delete_photos(
        session=db, gallery_id=gallery.id, photo_ids=fake_ids
    )

    assert deleted_count == 0


def test_get_photos_by_gallery_pagination(db: Session) -> None:
    """Test pagination for get_photos_by_gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create 10 photos
    for i in range(10):
        photo_in = PhotoCreate(
            gallery_id=gallery.id,
            filename=f"photo-{i}.jpg",
            url=f"/api/v1/galleries/{gallery.id}/photos/photo-{i}.jpg",
            file_size=1024,
        )
        crud.create_photo(session=db, photo_in=photo_in)

    # Test pagination: skip=0, limit=5
    photos = crud.get_photos_by_gallery(
        session=db, gallery_id=gallery.id, skip=0, limit=5
    )
    assert len(photos) == 5

    # Test pagination: skip=5, limit=5
    photos = crud.get_photos_by_gallery(
        session=db, gallery_id=gallery.id, skip=5, limit=5
    )
    assert len(photos) == 5

    # Test pagination: skip=10, limit=5 (should return empty)
    photos = crud.get_photos_by_gallery(
        session=db, gallery_id=gallery.id, skip=10, limit=5
    )
    assert len(photos) == 0

