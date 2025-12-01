"""API route tests for organization invitations"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    OrganizationCreate,
    OrganizationInvitationCreate,
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


def test_create_invitation(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating an organization invitation"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Create invitation
    data = {"email": "invitee@example.com"}
    r = client.post(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    invitation = r.json()
    assert invitation["email"] == "invitee@example.com"
    assert invitation["organization_id"] == str(org.id)


def test_create_invitation_duplicate(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that duplicate invitations are rejected"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Create first invitation
    data = {"email": "invitee@example.com"}
    r = client.post(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers,
        json=data,
    )
    assert r.status_code == 200

    # Try to create duplicate
    r = client.post(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 400
    assert "already been sent" in r.json()["detail"]


def test_get_invitations(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving invitations"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Create invitations
    for i in range(3):
        data = {"email": f"invitee{i}@example.com"}
        client.post(
            f"{settings.API_V1_STR}/invitations/",
            headers=headers,
            json=data,
        )

    # Get invitations
    r = client.get(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers,
    )

    assert r.status_code == 200
    invitations = r.json()
    assert invitations["count"] >= 3
    assert len(invitations["data"]) >= 3


def test_delete_invitation(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting an invitation"""
    # Create organization
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )

    # Create team member
    headers = create_test_team_member(client, db, org.id)

    # Create invitation
    data = {"email": "invitee@example.com"}
    r = client.post(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers,
        json=data,
    )
    invitation_id = r.json()["id"]

    # Delete invitation
    r = client.delete(
        f"{settings.API_V1_STR}/invitations/{invitation_id}",
        headers=headers,
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Invitation deleted"


def test_delete_invitation_not_own(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that users cannot delete invitations from other organizations"""
    # Create two organizations
    org1 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 1")
    )
    org2 = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Org 2")
    )

    # Create team member in org1
    headers1 = create_test_team_member(client, db, org1.id)

    # Create team member in org2
    headers2 = create_test_team_member(client, db, org2.id)

    # Create invitation in org2
    data = {"email": "invitee@example.com"}
    r = client.post(
        f"{settings.API_V1_STR}/invitations/",
        headers=headers2,
        json=data,
    )
    invitation_id = r.json()["id"]

    # Try to delete as org1 member
    r = client.delete(
        f"{settings.API_V1_STR}/invitations/{invitation_id}",
        headers=headers1,
    )

    assert r.status_code == 403
    assert "Not enough permissions" in r.json()["detail"]

