from collections.abc import Generator
from contextlib import nullcontext

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers, patch_password_hashing


@pytest.fixture(scope="module", autouse=True)
def disable_password_hashing(request: FixtureRequest) -> Generator[None, None, None]:
    """Fixture disabling password hashing

    Password hashing can be enabled on module level by marking the module with `pytest.mark.enable_password_hashing`.
    """

    with (
        patch_password_hashing("app.core.security")
        if all(m.name != "enable_password_hashing" for m in request.node.iter_markers())
        else nullcontext()
    ):
        yield


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    """
    Module scoped fixture providing a database session initialized with `init_db`.
    """
    with Session(engine) as session:
        yield session
        # Cleanup test database
        session.execute(delete(Item))
        session.execute(delete(User))
        session.commit()


@pytest.fixture(scope="module", autouse=True)
def init_db_fixture(db: Session) -> None:
    # note: deleting all users here is required to enable or disable password hashing per test module.
    # If we don't delete all users here, the users created during `init_db` will not be re-created and the password will stay (un)hashed,
    # leading to possibly failing tests relying on the created user for authentication.
    db.execute(delete(Item))
    db.execute(delete(User))
    init_db(db)
    db.commit()


@pytest.fixture(scope="module")
def client(db: Session) -> Generator[TestClient, None, None]:  # noqa: ARG001
    """
    Module scoped fixture providing a `TestClient` instance.

    NOTE: This fixture uses the `db` fixture WITHOUT hashing passwords!
    """
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
