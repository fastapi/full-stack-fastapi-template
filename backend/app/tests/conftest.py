"""
Testing configuration.

This module provides fixtures for testing.
"""
from collections.abc import Generator
from contextlib import contextmanager
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine
from app.main import app
from app.models import Item, User
from app.modules.users.services.user_service import UserService
from app.modules.users.repository.user_repo import UserRepository
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@contextmanager
def get_test_db() -> Generator[Session, None, None]:
    """
    Get a database session for testing.
    
    Yields:
        Database session
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """
    Database fixture for testing.
    
    This fixture sets up the database for testing and cleans up after tests.
    
    Yields:
        Database session
    """
    with Session(engine) as session:
        # Create initial data for testing
        _create_initial_test_data(session)
        
        yield session
        
        # Clean up test data
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


def _create_initial_test_data(session: Session) -> None:
    """
    Create initial data for testing.
    
    Args:
        session: Database session
    """
    # Create initial superuser if not exists
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    user_service.create_initial_superuser()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Test client fixture.
    
    Yields:
        Test client
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    """
    Superuser token headers fixture.
    
    Args:
        client: Test client
        
    Returns:
        Headers with superuser token
    """
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    """
    Normal user token headers fixture.
    
    Args:
        client: Test client
        db: Database session
        
    Returns:
        Headers with normal user token
    """
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
def user_service(db: Session) -> UserService:
    """
    User service fixture.
    
    Args:
        db: Database session
        
    Returns:
        User service instance
    """
    user_repo = UserRepository(db)
    return UserService(user_repo)