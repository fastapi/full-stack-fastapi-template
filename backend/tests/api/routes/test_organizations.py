"""API route tests for organizations"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import OrganizationCreate, OrganizationUpdate, UserCreate
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


def create_test_team_member_no_org(
    client: TestClient, db: Session
) -> dict[str, str]:
    """Create a test team member without an organization"""
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="team_member",
            organization_id=None,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return headers


def create_test_team_member_with_org(
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


def test_create_organization(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating an organization"""
    # Create team member without org
    headers = create_test_team_member_no_org(client, db)

    # Create organization
    data = {
        "name": "Test Organization",
        "description": "Test description",
    }
    r = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    org = r.json()
    assert org["name"] == "Test Organization"
    assert org["description"] == "Test description"


def test_create_organization_already_has_org(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that users with an organization cannot create another"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member with org
    headers = create_test_team_member_with_org(client, db, org.id)

    # Try to create another organization
    data = {
        "name": "Another Organization",
        "description": "Test",
    }
    r = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 400
    assert "already belong to an organization" in r.json()["detail"]


def test_get_organization(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving an organization"""
    # Create organization
    org = crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(
            name="Test Organization", description="Test"
        ),
    )

    # Create team member with org
    headers = create_test_team_member_with_org(client, db, org.id)

    # Get organization
    r = client.get(
        f"{settings.API_V1_STR}/organizations/{org.id}",
        headers=headers,
    )

    assert r.status_code == 200
    retrieved_org = r.json()
    assert retrieved_org["name"] == "Test Organization"
    assert retrieved_org["id"] == str(org.id)


def test_get_organization_not_own(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that users cannot view other organizations"""
    # Create two organizations
    org1 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 1")
    )
    org2 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 2")
    )

    # Create team member in org1
    headers = create_test_team_member_with_org(client, db, org1.id)

    # Try to get org2
    r = client.get(
        f"{settings.API_V1_STR}/organizations/{org2.id}",
        headers=headers,
    )

    assert r.status_code == 403
    assert "Not enough permissions" in r.json()["detail"]


def test_update_organization(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating an organization"""
    # Create organization
    org = crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(
            name="Original Name", description="Original"
        ),
    )

    # Create team member with org
    headers = create_test_team_member_with_org(client, db, org.id)

    # Update organization
    data = {"name": "Updated Name", "description": "Updated"}
    r = client.put(
        f"{settings.API_V1_STR}/organizations/{org.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_org = r.json()
    assert updated_org["name"] == "Updated Name"
    assert updated_org["description"] == "Updated"


def test_update_organization_not_own(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that users cannot update other organizations"""
    # Create two organizations
    org1 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 1")
    )
    org2 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 2")
    )

    # Create team member in org1
    headers = create_test_team_member_with_org(client, db, org1.id)

    # Try to update org2
    data = {"name": "Hacked Name"}
    r = client.put(
        f"{settings.API_V1_STR}/organizations/{org2.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 403
    assert "Not enough permissions" in r.json()["detail"]

