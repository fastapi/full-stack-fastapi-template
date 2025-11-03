"""Unit tests for Gallery CRUD operations"""

from datetime import date

from sqlmodel import Session

from app import crud
from app.models import GalleryCreate, GalleryUpdate, OrganizationCreate, ProjectCreate
from tests.utils.utils import random_lower_string


def test_create_gallery(db: Session) -> None:
    """Test creating a new gallery"""
    # Create organization and project first
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)

    project_in = ProjectCreate(
        name="Test Project", client_name="Test Client", organization_id=organization.id
    )
    project = crud.create_project(session=db, project_in=project_in)

    # Create gallery
    gallery_name = f"Test Gallery {random_lower_string()}"
    gallery_in = GalleryCreate(
        name=gallery_name,
        date=date.today(),
        photo_count=50,
        photographer="Test Photographer",
        status="published",
        cover_image_url="https://example.com/image.jpg",
        project_id=project.id,
    )

    gallery = crud.create_gallery(session=db, gallery_in=gallery_in)

    assert gallery.name == gallery_name
    assert gallery.photo_count == 50
    assert gallery.photographer == "Test Photographer"
    assert gallery.status == "published"
    assert gallery.project_id == project.id
    assert gallery.id is not None


def test_get_gallery(db: Session) -> None:
    """Test retrieving a gallery by ID"""
    # Setup: create org, project, and gallery
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    gallery_in = GalleryCreate(
        name="Test Gallery", photo_count=100, status="draft", project_id=project.id
    )
    created_gallery = crud.create_gallery(session=db, gallery_in=gallery_in)

    # Test retrieval
    retrieved_gallery = crud.get_gallery(session=db, gallery_id=created_gallery.id)

    assert retrieved_gallery is not None
    assert retrieved_gallery.id == created_gallery.id
    assert retrieved_gallery.name == "Test Gallery"
    assert retrieved_gallery.photo_count == 100


def test_update_gallery(db: Session) -> None:
    """Test updating a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
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
            name="Original Name", photo_count=50, status="draft", project_id=project.id
        ),
    )

    # Update gallery
    gallery_update = GalleryUpdate(
        name="Updated Name", photo_count=100, status="published"
    )

    updated_gallery = crud.update_gallery(
        session=db, db_gallery=gallery, gallery_in=gallery_update
    )

    assert updated_gallery.name == "Updated Name"
    assert updated_gallery.photo_count == 100
    assert updated_gallery.status == "published"


def test_get_galleries_by_project(db: Session) -> None:
    """Test retrieving all galleries for a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )

    # Create multiple galleries
    for i in range(3):
        crud.create_gallery(
            session=db,
            gallery_in=GalleryCreate(
                name=f"Gallery {i}", photo_count=i * 10, project_id=project.id
            ),
        )

    # Retrieve galleries
    galleries = crud.get_galleries_by_project(session=db, project_id=project.id)

    assert len(galleries) == 3
    gallery_names = [g.name for g in galleries]
    assert "Gallery 0" in gallery_names
    assert "Gallery 1" in gallery_names
    assert "Gallery 2" in gallery_names


def test_delete_gallery(db: Session) -> None:
    """Test deleting a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
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
            name="Gallery to Delete", photo_count=50, project_id=project.id
        ),
    )
    gallery_id = gallery.id

    # Verify gallery exists
    assert crud.get_gallery(session=db, gallery_id=gallery_id) is not None

    # Delete gallery
    crud.delete_gallery(session=db, gallery_id=gallery_id)

    # Verify gallery is deleted
    assert crud.get_gallery(session=db, gallery_id=gallery_id) is None
