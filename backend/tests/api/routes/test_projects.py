"""API route tests for projects"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    OrganizationCreate,
    ProjectCreate,
    ProjectUpdate,
    UserCreate,
)
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


def create_test_team_member(
    client: TestClient, db: Session, org_id: uuid.UUID
) -> dict[str, str]:
    """Create a test team member user and return token headers"""
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="team_member",
            organization_id=org_id,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return headers


def create_test_client(
    client: TestClient, db: Session, project_id: uuid.UUID
) -> dict[str, str]:
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
    return headers


def test_create_project_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a project as a team member"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Create project
    data = {
        "name": "Test Project",
        "client_name": "Test Client",
        "status": "planning",
        "organization_id": str(org.id),
    }
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    project = r.json()
    assert project["name"] == "Test Project"
    assert project["organization_id"] == str(org.id)


def test_create_project_client_forbidden(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that clients cannot create projects"""
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
    headers = create_test_client(client, db, project.id)

    # Try to create project
    data = {
        "name": "Unauthorized Project",
        "client_name": "Client",
        "organization_id": str(org.id),
    }
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 403
    assert "Only team members" in r.json()["detail"]


def test_get_projects_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving projects as a team member"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create projects
    for i in range(3):
        crud.create_project(
            session=db,
            project_in=ProjectCreate(
                name=f"Project {i}",
                client_name=f"Client {i}",
                organization_id=org.id,
            ),
        )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Get projects
    r = client.get(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
    )

    assert r.status_code == 200
    projects = r.json()
    assert projects["count"] >= 3
    assert len(projects["data"]) >= 3


def test_get_projects_client(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving projects as a client"""
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

    # Create client with access
    headers = create_test_client(client, db, project.id)

    # Get projects
    r = client.get(
        f"{settings.API_V1_STR}/projects/",
        headers=headers,
    )

    assert r.status_code == 200
    projects = r.json()
    assert projects["count"] >= 1
    assert len(projects["data"]) >= 1


def test_get_project_by_id(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving a project by ID"""
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

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Get project
    r = client.get(
        f"{settings.API_V1_STR}/projects/{project.id}",
        headers=headers,
    )

    assert r.status_code == 200
    retrieved_project = r.json()
    assert retrieved_project["name"] == "Test Project"
    assert retrieved_project["id"] == str(project.id)


def test_update_project(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Original Name",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Update project
    data = {"name": "Updated Name", "status": "in_progress"}
    r = client.put(
        f"{settings.API_V1_STR}/projects/{project.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_project = r.json()
    assert updated_project["name"] == "Updated Name"
    assert updated_project["status"] == "in_progress"


def test_delete_project(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project to Delete",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Delete project
    r = client.delete(
        f"{settings.API_V1_STR}/projects/{project.id}",
        headers=headers,
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Project deleted successfully"

    # Verify project is deleted
    deleted_project = crud.get_project(session=db, project_id=project.id)
    assert deleted_project is None


def test_get_dashboard_stats(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test getting dashboard stats"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Get stats
    r = client.get(
        f"{settings.API_V1_STR}/projects/stats",
        headers=headers,
    )

    assert r.status_code == 200
    stats = r.json()
    assert "active_projects" in stats
    assert "upcoming_deadlines" in stats
    assert "team_members" in stats
    assert "completed_this_month" in stats


def test_get_dashboard_stats_client_forbidden(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that clients cannot get dashboard stats"""
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

    # Create client
    headers = create_test_client(client, db, project.id)

    # Try to get stats
    r = client.get(
        f"{settings.API_V1_STR}/projects/stats",
        headers=headers,
    )

    assert r.status_code == 403
    assert "Dashboard stats only available to team members" in r.json()["detail"]

