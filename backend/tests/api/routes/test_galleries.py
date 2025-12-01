"""API route tests for galleries"""

import uuid
from io import BytesIO

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    Gallery,
    GalleryCreate,
    OrganizationCreate,
    PhotoCreate,
    ProjectCreate,
    User,
    UserCreate,
)
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


def create_test_team_member(
    client: TestClient, db: Session
) -> tuple[User, dict[str, str]]:
    """Create a test team member user and return user and token headers"""
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="team_member",
            organization_id=org.id,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return user, headers


def create_test_client(
    client: TestClient, db: Session, project_id: uuid.UUID
) -> tuple[User, dict[str, str]]:
    """Create a test client user with access to a project"""
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="client",
        ),
    )
    # Grant access to project
    from app.models import ProjectAccessCreate

    crud.create_project_access(
        session=db,
        access_in=ProjectAccessCreate(
            project_id=project_id,
            user_id=user.id,
            role="viewer",
            can_comment=True,
            can_download=True,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return user, headers


def test_create_gallery_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a gallery as a team member"""
    # Create organization and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    user, headers = create_test_team_member(client, db)
    # Update user's organization
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Create gallery
    data = {
        "name": "Test Gallery",
        "photo_count": 0,
        "status": "draft",
        "project_id": str(project.id),
    }
    r = client.post(
        f"{settings.API_V1_STR}/galleries/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    gallery = r.json()
    assert gallery["name"] == "Test Gallery"
    assert gallery["project_id"] == str(project.id)


def test_create_gallery_client_forbidden(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that clients cannot create galleries"""
    # Create organization and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create client
    user, headers = create_test_client(client, db, project.id)

    # Try to create gallery
    data = {
        "name": "Test Gallery",
        "photo_count": 0,
        "status": "draft",
        "project_id": str(project.id),
    }
    r = client.post(
        f"{settings.API_V1_STR}/galleries/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 403
    assert "Only team members" in r.json()["detail"]


def test_get_gallery(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Get gallery
    r = client.get(
        f"{settings.API_V1_STR}/galleries/{gallery.id}",
        headers=headers,
    )

    assert r.status_code == 200
    retrieved_gallery = r.json()
    assert retrieved_gallery["name"] == "Test Gallery"
    assert retrieved_gallery["id"] == str(gallery.id)


def test_get_galleries_by_project(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving galleries for a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create galleries
    for i in range(3):
        crud.create_gallery(
            session=db,
            gallery_in=GalleryCreate(
                name=f"Gallery {i}", photo_count=0, project_id=project.id
            ),
        )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Get galleries
    r = client.get(
        f"{settings.API_V1_STR}/galleries/?project_id={project.id}",
        headers=headers,
    )

    assert r.status_code == 200
    galleries = r.json()
    assert galleries["count"] >= 3
    assert len(galleries["data"]) >= 3


def test_upload_photo_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test uploading photos as a team member"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Upload photo
    file_content = b"fake image content"
    files = {"files": ("test.jpg", BytesIO(file_content), "image/jpeg")}

    r = client.post(
        f"{settings.API_V1_STR}/galleries/{gallery.id}/photos",
        headers=headers,
        files=files,
    )

    assert r.status_code == 200
    photos = r.json()
    assert photos["count"] == 1
    assert len(photos["data"]) == 1
    assert photos["data"][0]["filename"] == "test.jpg"


def test_upload_photo_client_forbidden(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that clients cannot upload photos"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create client
    user, headers = create_test_client(client, db, project.id)

    # Try to upload photo
    file_content = b"fake image content"
    files = {"files": ("test.jpg", BytesIO(file_content), "image/jpeg")}

    r = client.post(
        f"{settings.API_V1_STR}/galleries/{gallery.id}/photos",
        headers=headers,
        files=files,
    )

    assert r.status_code == 403
    assert "Only team members" in r.json()["detail"]


def test_list_gallery_photos(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test listing photos in a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create photos
    for i in range(3):
        photo = crud.create_photo(
            session=db,
            photo_in=PhotoCreate(
                gallery_id=gallery.id,
                filename=f"photo-{i}.jpg",
                url=f"/api/v1/galleries/{gallery.id}/photos/photo-{i}.jpg",
                file_size=1024,
            ),
        )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # List photos
    r = client.get(
        f"{settings.API_V1_STR}/galleries/{gallery.id}/photos",
        headers=headers,
    )

    assert r.status_code == 200
    photos = r.json()
    assert photos["count"] == 3
    assert len(photos["data"]) == 3


def test_delete_gallery_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting a gallery as a team member"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Test Gallery", photo_count=0, project_id=project.id
        ),
    )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Delete gallery
    r = client.delete(
        f"{settings.API_V1_STR}/galleries/{gallery.id}",
        headers=headers,
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Gallery deleted successfully"

    # Verify gallery is deleted
    deleted_gallery = db.get(Gallery, gallery.id)
    assert deleted_gallery is None


def test_update_gallery(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating a gallery"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )
    gallery = crud.create_gallery(
        session=db,
        gallery_in=GalleryCreate(
            name="Original Name", photo_count=0, project_id=project.id
        ),
    )

    # Create team member
    user, headers = create_test_team_member(client, db)
    user.organization_id = org.id
    db.add(user)
    db.commit()

    # Update gallery
    data = {"name": "Updated Name", "status": "published"}
    r = client.put(
        f"{settings.API_V1_STR}/galleries/{gallery.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_gallery = r.json()
    assert updated_gallery["name"] == "Updated Name"
    assert updated_gallery["status"] == "published"

