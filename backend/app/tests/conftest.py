from collections.abc import Generator
from unittest.mock import patch

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="module")
def disable_password_hashing(request: FixtureRequest) -> Generator[bool, None, None]:
    """
    Disable password hashing if no `enable_password_hashing` marker set for module.
    """

    module = request.node.getparent(pytest.Module)
    if not module.get_closest_marker("enable_password_hashing"):
        with (
            patch("app.core.security.pwd_context.verify", lambda x, y: x == y),
            patch("app.core.security.pwd_context.hash", lambda x: x),
        ):
            yield True
    else:
        yield False  # Don't patch if `enable_password_hashing` marker is set


@pytest.fixture(scope="module", autouse=True)
def db(disable_password_hashing: bool) -> Generator[Session, None, None]:  # noqa: ARG001
    with Session(engine) as session:
        session.execute(  # Recreate user for every module, with\without pwd hashing
            delete(User)
        )
        init_db(session)
        session.commit()
        yield session
        # Cleanup test database
        session.execute(delete(Item))
        session.execute(delete(User))
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
