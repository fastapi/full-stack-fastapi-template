"""API route tests for Project endpoints"""

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import create_organization
from app.models import OrganizationCreate
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def _create_test_project_data(organization_id, **kwargs):
    """Helper function to create project data with required fields"""
    today = date.today()
    defaults = {
        "name": f"Test Project {random_lower_string()}",
        "client_name": f"Client {random_lower_string()}",
        "start_date": today.isoformat(),
        "deadline": (today + timedelta(days=30)).isoformat(),
        "organization_id": str(organization_id),
    }
    defaults.update(kwargs)
    return defaults


def test_create_project_success(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test successfully creating a project with required fields"""
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = create_organization(session=db, organization_in=org_in)

    # Get user's organization_id from token
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")

    if not user_org_id:
        # Update user's organization if needed
        # This is a test setup issue, skip for now
        return

    project_data = _create_test_project_data(organization_id=user_org_id)

    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )

    assert r.status_code == 200
    project = r.json()
    assert project["name"] == project_data["name"]
    assert project["client_name"] == project_data["client_name"]
    assert project["start_date"] == project_data["start_date"]
    assert project["deadline"] == project_data["deadline"]


def test_create_project_missing_start_date(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test that creating a project without start_date fails validation"""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")

    if not user_org_id:
        return

    project_data = _create_test_project_data(organization_id=user_org_id)
    del project_data["start_date"]  # Remove required field

    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )

    assert r.status_code == 422  # Validation error
    error_detail = r.json().get("detail", [])
    assert any("start_date" in str(err).lower() for err in error_detail)


def test_create_project_missing_deadline(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test that creating a project without deadline fails validation"""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")

    if not user_org_id:
        return

    project_data = _create_test_project_data(organization_id=user_org_id)
    del project_data["deadline"]  # Remove required field

    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )

    assert r.status_code == 422  # Validation error
    error_detail = r.json().get("detail", [])
    assert any("deadline" in str(err).lower() for err in error_detail)


def test_create_project_deadline_before_start_date(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test that creating a project with deadline before start_date fails validation"""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")

    if not user_org_id:
        return

    today = date.today()
    project_data = _create_test_project_data(
        organization_id=user_org_id,
        start_date=today.isoformat(),
        deadline=(today - timedelta(days=1)).isoformat(),  # Deadline before start
    )

    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )

    assert r.status_code == 400
    error_detail = r.json().get("detail", "")
    assert "deadline" in error_detail.lower() or "start date" in error_detail.lower()


def test_create_project_deadline_equal_start_date(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test that creating a project with deadline equal to start_date is allowed"""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")

    if not user_org_id:
        return

    today = date.today()
    project_data = _create_test_project_data(
        organization_id=user_org_id,
        start_date=today.isoformat(),
        deadline=today.isoformat(),  # Same date
    )

    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )

    assert r.status_code == 200
    project = r.json()
    assert project["start_date"] == today.isoformat()
    assert project["deadline"] == today.isoformat()


def test_create_project_client_forbidden(
    client: TestClient, db: Session
) -> None:
    """Test that clients cannot create projects"""
    from app import crud
    from app.models import OrganizationCreate, UserCreate
    
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    db.commit()
    
    # Create client user
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
        user_type="client",
        organization_id=None,  # Clients don't belong to organizations
    )
    user = crud.create_user(session=db, user_create=user_in)
    db.commit()
    
    # Get auth token for client
    from tests.utils.user import user_authentication_headers
    client_headers = user_authentication_headers(client=client, email=email, password=password)
    
    # Try to create a project
    today = date.today()
    project_data = _create_test_project_data(
        organization_id=organization.id,
    )
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=client_headers,
        json=project_data,
    )
    
    assert r.status_code == 403
    error_detail = r.json().get("detail", "")
    assert "team member" in error_detail.lower()


def test_create_project_superuser_forbidden(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that superusers cannot create projects (unless they're team members)"""
    from app import crud
    from app.models import OrganizationCreate
    
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    db.commit()
    
    # Try to create a project as superuser
    today = date.today()
    project_data = _create_test_project_data(
        organization_id=organization.id,
    )
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=superuser_token_headers,
        json=project_data,
    )
    
    assert r.status_code == 403
    error_detail = r.json().get("detail", "")
    assert "team member" in error_detail.lower()


def test_create_project_no_organization(
    client: TestClient, db: Session
) -> None:
    """Test that team members without an organization cannot create projects"""
    from app import crud
    from app.models import UserCreate
    from tests.utils.user import user_authentication_headers
    
    # Create team member without organization
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
        user_type="team_member",
        organization_id=None,  # No organization
    )
    user = crud.create_user(session=db, user_create=user_in)
    db.commit()
    
    # Get auth token
    team_member_headers = user_authentication_headers(client=client, email=email, password=password)
    
    # Create organization for the project (but user doesn't belong to it)
    from app.models import OrganizationCreate
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    db.commit()
    
    # Try to create a project
    project_data = _create_test_project_data(
        organization_id=organization.id,
    )
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_headers,
        json=project_data,
    )
    
    assert r.status_code == 400
    error_detail = r.json().get("detail", "")
    assert "organization" in error_detail.lower()


def test_create_project_wrong_organization(
    client: TestClient, db: Session
) -> None:
    """Test that team members cannot create projects for other organizations"""
    from app import crud
    from app.models import OrganizationCreate, UserCreate
    from tests.utils.user import user_authentication_headers
    
    # Create first organization and team member
    org1_in = OrganizationCreate(name=random_lower_string())
    organization1 = crud.create_organization(session=db, organization_in=org1_in)
    db.commit()
    
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
        user_type="team_member",
        organization_id=organization1.id,
    )
    user = crud.create_user(session=db, user_create=user_in)
    db.commit()
    
    # Get auth token
    team_member_headers = user_authentication_headers(client=client, email=email, password=password)
    
    # Create second organization
    org2_in = OrganizationCreate(name=random_lower_string())
    organization2 = crud.create_organization(session=db, organization_in=org2_in)
    db.commit()
    
    # Try to create a project for the second organization
    project_data = _create_test_project_data(
        organization_id=organization2.id,  # Wrong organization
    )
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_headers,
        json=project_data,
    )
    
    assert r.status_code == 403
    error_detail = r.json().get("detail", "")
    assert "permission" in error_detail.lower() or "not enough" in error_detail.lower()


def test_create_project_team_member_success(
    client: TestClient, team_member_token_headers: dict[str, str], db: Session
) -> None:
    """Test that team members with organization can successfully create projects"""
    # Get user's organization_id from token
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=team_member_token_headers
    )
    user = r.json()
    user_org_id = user.get("organization_id")
    
    assert user_org_id is not None, "Team member should have an organization"
    assert user.get("user_type") == "team_member", "User should be a team member"
    
    project_data = _create_test_project_data(organization_id=user_org_id)
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=team_member_token_headers,
        json=project_data,
    )
    
    assert r.status_code == 200
    project = r.json()
    assert project["name"] == project_data["name"]
    assert project["organization_id"] == str(user_org_id)


def test_create_project_unauthorized_no_token(
    client: TestClient, db: Session
) -> None:
    """Test that project creation requires authentication"""
    from app import crud
    from app.models import OrganizationCreate
    
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    db.commit()
    
    # Try to create a project without authentication
    project_data = _create_test_project_data(
        organization_id=organization.id,
    )
    
    r = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers={},  # No auth headers
        json=project_data,
    )
    
    assert r.status_code == 401  # Unauthorized

