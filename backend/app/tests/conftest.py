from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers, patch_password_hashing


@pytest.fixture(scope="session")
def disable_password_hashing() -> Generator[None, None, None]:
    with patch_password_hashing("app.core.security"):
        yield


@pytest.fixture(scope="session", autouse=True)
def db(
    disable_password_hashing: Generator[None, None, None],  # noqa: ARG001
) -> Generator[Session, None, None]:
    with Session(engine) as session:
        # cleanup db to prevent interferences with tests
        # all existing data will be deleted anyway after the tests run
        session.execute(delete(User))
        session.execute(delete(Item))
        session.commit()

        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


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
