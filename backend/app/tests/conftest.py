from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from app.api.deps import get_session
from app.core.config import settings
from app.core.db import init_db
from app.main import app
from app.models import Item, User
from app.repositories.items import ItemRepository
from app.repositories.users import UserRepository
from app.services.items import ItemService
from app.services.users import UserService
from app.tests.utils.item import create_random_item
from app.tests.utils.user import (
    create_random_user,
    get_authentication_token_from_email,
    get_superuser_token_headers,
)


@pytest.fixture(scope="session", autouse=True)
def test_engine() -> Generator[Engine, None, None]:
    """Creates clean test database for e2e test requests"""
    test_engine = create_engine(str(settings.SQLALCHEMY_TEST_DATABASE_URI))
    SQLModel.metadata.drop_all(bind=test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def session(test_engine: Engine) -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        init_db(session)
        yield session


@pytest.fixture(scope="module", name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """overrides session Dependency for TestClient Repositories with postgres test session"""

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, session: Session) -> dict[str, str]:
    return get_authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, session=session
    )


@pytest.fixture(autouse=True)
def mock_retry() -> Generator[MagicMock | AsyncMock, None, None]:
    with patch("app.backend_pre_start.retry") as MockRetry:
        # MockRetry.wait = wait_none()
        MockRetry.side_effect = lambda *args, **kwargs: lambda func: func
        yield MockRetry


@pytest.fixture(scope="module")
def user_repository(session: Session) -> UserRepository:
    return UserRepository(session=session)


@pytest.fixture(scope="module")
def user_service(user_repository: UserRepository) -> UserService:
    return UserService(repository=user_repository)


@pytest.fixture
def user(session: Session) -> User:
    return create_random_user(session)


@pytest.fixture(scope="module")
def item_repository(session: Session) -> ItemRepository:
    return ItemRepository(session=session)


@pytest.fixture(scope="module")
def item_service(item_repository: ItemRepository) -> ItemService:
    return ItemService(repository=item_repository)


@pytest.fixture
def item(session: Session) -> Item:
    return create_random_item(session)
