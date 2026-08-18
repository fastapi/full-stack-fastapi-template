from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User, UserRole
from tests.utils.user import authentication_token_from_email, authentication_token_for_role
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
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
def manager_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_for_role(
        client=client,
        db=db,
        email=settings.MANAGER_USER,
        password=settings.MANAGER_USER_PASSWORD,
        role=UserRole.MANAGER,
    )


@pytest.fixture(scope="module")
def member_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_for_role(
        client=client,
        db=db,
        email=settings.MEMBER_USER,
        password=settings.MEMBER_USER_PASSWORD,
        role=UserRole.MEMBER,
    )
