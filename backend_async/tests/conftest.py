from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.db import init_db
from app.models import Item, User
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers

from app.api.deps import get_db

test_engine = create_async_engine(
    url=str(settings.SQLALCHEMY_TEST_DATABASE_URI),
    # echo=True
)

# test db dependency to override the default db session
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=test_engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session", autouse=True)
async def db() -> AsyncGenerator[AsyncSession, None]:
    from sqlmodel import SQLModel, create_engine
    SQLModel.metadata.create_all(
        create_engine(url = str(settings.SQLALCHEMY_TEST_DATABASE_URI))
    )
    async with AsyncSession(test_engine) as session:
        await init_db(session)
        yield session
        statement = delete(Item)
        await session.exec(statement)
        statement = delete(User)
        await session.exec(statement)
        await session.commit()


@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = get_test_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac


@pytest.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> dict[str, str]:
    return await get_superuser_token_headers(client)


@pytest.fixture(scope="module")
async def normal_user_token_headers(client: AsyncClient, db: AsyncSession) -> dict[str, str]:
    return await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )

