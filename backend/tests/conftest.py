from collections.abc import Generator
from typing import Generator as TypingGenerator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.db import engine as default_engine, init_db
from app.main import app
from app import api
from app.models import Item, User, Image, ImageVariant, ImageProcessingJob
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="function")
def db_engine():
    """Create fresh database engine for each test to ensure complete isolation."""
    # Use dedicated test database URL to separate from main database
    test_db_url = str(settings.TEST_DATABASE_URL)

    # Create engine with test-specific settings
    engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        echo=False,  # Disable SQL logging for tests
    )

    # Create all tables for each test
    from app.models import SQLModel
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup: Drop all tables after each test
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """Create transaction-isolated database session for each test."""
    # Bind the session to the engine
    with Session(bind=db_engine) as session:
        # Begin a transaction
        transaction = session.begin()

        # Initialize database with superuser for tests
        init_db(session)

        try:
            yield session
        finally:
            # Always rollback the transaction to ensure isolation
            try:
                transaction.rollback()
            except Exception:
                pass  # Ignore rollback errors

            # Explicit cleanup of session state
            session.expunge_all()


@pytest.fixture(scope="session")
def db_session_scope() -> Generator[Session, None, None]:
    """Session-scoped database fixture for backward compatibility (deprecated)."""
    with Session(default_engine) as session:
        init_db(session)
        yield session
        # Cleanup data at end of session
        statement = delete(ImageProcessingJob)
        session.execute(statement)
        statement = delete(ImageVariant)
        session.execute(statement)
        statement = delete(Image)
        session.execute(statement)
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database session override.
    This ensures each test gets an isolated database session.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Transaction will be rolled back by db fixture

    # Override the dependency
    app.dependency_overrides[api.deps.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Clean up overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
