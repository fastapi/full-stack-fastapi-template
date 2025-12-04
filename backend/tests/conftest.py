from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app import crud
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Organization, OrganizationCreate, User, UserCreate
from tests.utils.user import authentication_token_from_email, user_authentication_headers
from tests.utils.utils import get_superuser_token_headers, random_email, random_lower_string


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        # Clean up in proper order due to foreign key constraints
        try:
            statement = delete(User)
            session.execute(statement)
            statement = delete(Organization)
            session.execute(statement)
            session.commit()
        except Exception:
            # If cleanup fails, rollback to allow session to close cleanly
            session.rollback()
            raise


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
def team_member_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Create a team member user with an organization and return auth headers"""
    email = random_email()
    password = random_lower_string()
    
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    db.commit()
    
    # Create team member user
    user_in = UserCreate(
        email=email,
        password=password,
        user_type="team_member",
        organization_id=organization.id,
    )
    user = crud.create_user(session=db, user_create=user_in)
    db.commit()
    
    return user_authentication_headers(client=client, email=email, password=password)
