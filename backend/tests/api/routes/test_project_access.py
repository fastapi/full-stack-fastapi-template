"""API route tests for project access"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    OrganizationCreate,
    ProjectAccessCreate,
    ProjectAccessInviteByEmail,
    ProjectAccessUpdate,
    ProjectCreate,
    UserCreate,
)
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


def create_test_team_member(
    client: TestClient, db: Session, org_id: uuid.UUID
) -> dict[str, str]:
    """Create a test team member with an organization"""
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
) -> tuple[dict[str, str], uuid.UUID]:
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
    return headers, user.id


def test_invite_client_by_email(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test inviting a client by email"""
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

    # Invite client
    data = {
        "email": "newclient@example.com",
        "role": "viewer",
        "can_comment": True,
        "can_download": True,
    }
    r = client.post(
        f"{settings.API_V1_STR}/project-access/{project.id}/access/invite-by-email",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    response = r.json()
    assert "message" in response
    assert response["email"] == "newclient@example.com"


def test_invite_client_by_email_existing_user(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test inviting an existing user by email"""
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

    # Create existing client user
    existing_user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email="existing@example.com",
            password="password123",
            user_type="client",
        ),
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Invite existing user
    data = {
        "email": "existing@example.com",
        "role": "viewer",
        "can_comment": True,
        "can_download": True,
    }
    r = client.post(
        f"{settings.API_V1_STR}/project-access/{project.id}/access/invite-by-email",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    response = r.json()
    assert response["is_pending"] is False
    assert "access" in response


def test_get_project_access_list(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test getting list of users with project access"""
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

    # Create clients with access
    for i in range(2):
        user = crud.create_user(
            session=db,
            user_create=UserCreate(
                email=f"client{i}@example.com",
                password="password123",
                user_type="client",
            ),
        )
        crud.create_project_access(
            session=db,
            access_in=ProjectAccessCreate(
                project_id=project.id,
                user_id=user.id,
                role="viewer",
                can_comment=True,
                can_download=True,
            ),
        )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Get access list
    r = client.get(
        f"{settings.API_V1_STR}/project-access/{project.id}/access",
        headers=headers,
    )

    assert r.status_code == 200
    access_list = r.json()
    assert len(access_list) >= 2
    assert "user" in access_list[0]


def test_revoke_project_access(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test revoking project access"""
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

    # Create client with access
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email="client@example.com",
            password="password123",
            user_type="client",
        ),
    )
    crud.create_project_access(
        session=db,
        access_in=ProjectAccessCreate(
            project_id=project.id,
            user_id=user.id,
            role="viewer",
            can_comment=True,
            can_download=True,
        ),
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Revoke access
    r = client.delete(
        f"{settings.API_V1_STR}/project-access/{project.id}/access/{user.id}",
        headers=headers,
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Access revoked successfully"

    # Verify access is revoked
    has_access = crud.user_has_project_access(
        session=db, project_id=project.id, user_id=user.id
    )
    assert has_access is False


def test_update_project_access(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating project access permissions"""
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

    # Create client with access
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email="client@example.com",
            password="password123",
            user_type="client",
        ),
    )
    crud.create_project_access(
        session=db,
        access_in=ProjectAccessCreate(
            project_id=project.id,
            user_id=user.id,
            role="viewer",
            can_comment=True,
            can_download=True,
        ),
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Update access
    data = {"role": "collaborator", "can_comment": False, "can_download": True}
    r = client.patch(
        f"{settings.API_V1_STR}/project-access/{project.id}/access/{user.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_access = r.json()
    assert updated_access["role"] == "collaborator"
    assert updated_access["can_comment"] is False


def test_get_my_projects(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test getting current user's projects"""
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

    # Create client with access
    headers, _ = create_test_client(client, db, project.id)

    # Get my projects
    r = client.get(
        f"{settings.API_V1_STR}/project-access/my-projects",
        headers=headers,
    )

    assert r.status_code == 200
    projects = r.json()
    assert projects["count"] >= 1
    assert len(projects["data"]) >= 1

