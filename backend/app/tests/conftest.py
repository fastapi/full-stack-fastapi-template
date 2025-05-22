from collections.abc import Generator
import os
import logging
from typing import Dict, Generator, Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import init_db
from app.main import app
from app.models import Item, User, WorkoutPost, UserFollow, Workout, Exercise
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from app.tests.utils.test_client import TestClientWrapper, get_test_client_wrapper

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create a test database engine with in-memory SQLite for fast tests
@pytest.fixture(scope="session")
def test_engine():
    """Create a test SQLite engine for fast tests."""
    # Use in-memory SQLite for tests
    TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables in the test database
    SQLModel.metadata.create_all(engine)
    
    return engine


@pytest.fixture(scope="function")
def db(test_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    This fixture is function-scoped to isolate test data.
    """
    with Session(test_engine) as session:
        init_db(session)
        yield session
        
        # Clean up all test data after each test
        for model in [Exercise, Workout, WorkoutPost, UserFollow, Item, User]:
            statement = delete(model)
            session.execute(statement)
        
        session.commit()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a new FastAPI TestClient that uses the `db` fixture.
    """
    # Override the get_db dependency to use the test database
    def get_test_db():
        try:
            yield db
        finally:
            pass
    
    # Override the dependency
    app.dependency_overrides = {}  # Clear any existing overrides
    
    # Add test database override
    from app.api.deps import get_db
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency override after the test
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    """Get superuser token headers for authenticated requests."""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    """Get normal user token headers for authenticated requests."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
def test_app():
    """Return the FastAPI app for testing."""
    return app


@pytest.fixture(scope="function")
def test_client(client: TestClient) -> TestClientWrapper:
    """Return a TestClientWrapper for the test client."""
    return get_test_client_wrapper(client)
