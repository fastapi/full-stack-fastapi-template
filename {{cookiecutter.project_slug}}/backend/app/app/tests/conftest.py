from typing import Dict, Generator, AsyncGenerator
import asyncio
import pytest
import pytest_asyncio
from websockets.client import ClientConnection as Connect
# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.core.config import settings
# from app.db.session import SessionLocal
from app.db.session import async_session, engine_async
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from app.db.init_db import init_db
from app.db import base  # noqa: F401
from app.tests_pre_start import init


class WsTestClient(Connect):
    base_url = f"ws://localhost{settings.API_V1_STR}"

    def __init__(self, url) -> None:
        super().__init__(self.base_url + url)


@pytest_asyncio.fixture(scope="module")
async def async_get_db(event_loop) -> AsyncGenerator:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="module")
def ws_client() -> WsTestClient:
    return WsTestClient


@pytest_asyncio.fixture
async def client(event_loop) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def superuser_token_headers(event_loop, client: AsyncClient) -> Dict[str, str]:
    headers = await get_superuser_token_headers(client)
    return headers


@pytest_asyncio.fixture
async def normal_user_token_headers(client: AsyncClient, async_get_db: AsyncSession) -> Dict[str, str]:
    headers = await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=async_get_db
    )
    return headers


@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='module', autouse=True)
async def clear_db(async_get_db: AsyncSession) -> None:
    try:
        # Try to create session to check if DB is awake
        async with engine_async.begin() as conn:
            await conn.run_sync(base.Base.metadata.drop_all)
            await conn.run_sync(base.Base.metadata.create_all)
        await init_db(db=async_get_db)
        await async_get_db.execute("SELECT 1")
    except Exception as e:
        raise e
