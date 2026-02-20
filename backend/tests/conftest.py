from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_core import MultiHostUrl
from sqlalchemy import text
from sqlmodel import Session, create_engine

from app.auth.dependencies import get_db
from app.config import settings
from app.database import init_db
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers

TEST_POSTGRES_DB = settings.POSTGRES_DB + "_test"

TEST_DATABASE_URI = MultiHostUrl.build(
    scheme="postgresql+psycopg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_SERVER,
    port=settings.POSTGRES_PORT,
    path=TEST_POSTGRES_DB,
)

test_engine = create_engine(str(TEST_DATABASE_URI))


ADMIN_DATABASE_URI = MultiHostUrl.build(
    scheme="postgresql+psycopg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_SERVER,
    port=settings.POSTGRES_PORT,
    path="postgres",
)

admin_engine = create_engine(str(ADMIN_DATABASE_URI))


def create_test_database() -> None:
    """Create the test database by copying the existing database."""
    # AUTOCOMMIT is required to drop a database
    with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_POSTGRES_DB}"'))
        conn.execute(
            text(
                f'CREATE DATABASE "{TEST_POSTGRES_DB}" WITH TEMPLATE "{settings.POSTGRES_DB}"',
            ),
        )


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session]:
    create_test_database()
    with Session(test_engine) as session:
        init_db(session)
        yield session
    with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_POSTGRES_DB}"'))


def get_test_db() -> Generator[Session]:
    """Database dependency override for testing."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        db=db,
    )
