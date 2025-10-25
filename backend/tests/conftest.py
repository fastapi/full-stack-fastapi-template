from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from app.api.deps import get_db
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def test_engine() -> Generator[Engine, Any, None]:
    """
    Session-scoped fixture that creates tables and initializes test database.
    Follows official SQLModel testing pattern for FastAPI applications.
    """
    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Initialize database with superuser once for all tests
    with Session(engine) as init_session:
        init_db(init_session)
        init_session.commit()

    yield engine

    # Cleanup: drop all tables after test session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(test_engine: Engine) -> Generator[Session, None, None]:
    """
    Function-scoped fixture that provides a fresh database session for each test.
    This ensures test isolation and prevents data contamination between tests.
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    """
    Function-scoped fixture that provides a TestClient with overridden database dependency.

    This ensures that both:
    1. Direct database operations in tests (via session fixture)
    2. API calls through TestClient

    Use the SAME session, guaranteeing transaction visibility and consistency.
    This follows the official SQLModel + FastAPI testing pattern.
    """

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_db] = get_session_override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for superuser."""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    """Get authentication headers for normal test user."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=session
    )


# Backward compatibility alias
db = session
