from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """
    Session-scoped database fixture following official FastAPI template pattern.

    For PostgreSQL testing (Supabase production parity):
    - Creates tables once per test session
    - Initializes superuser (committed via crud.create_user)
    - Yields session for all tests
    - Cleans up after all tests complete
    """
    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Initialize database in separate session that commits and closes
    with Session(engine) as init_session:
        init_db(init_session)  # Creates superuser and commits (via crud.create_user)
    # init_session closes here, releasing connection to pool

    # Yield a fresh session for tests
    with Session(engine) as session:
        yield session

    # Cleanup: drop all tables after test session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Module-scoped TestClient fixture.

    Uses app's natural get_db() dependency without override.
    This works because PostgreSQL connections pool properly and
    committed data is visible across all sessions.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for superuser (cached per module)."""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Get authentication headers for normal test user (cached per module)."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
