import asyncio
from typing import AsyncGenerator, Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
async def db(event_loop) -> AsyncGenerator:
    async with async_session() as session:
        yield session


@pytest.fixture(scope="module")
async def client(event_loop) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture(scope="module")
async def superuser_token_headers(event_loop, client: AsyncClient) -> Dict[str, str]:
    headers = await get_superuser_token_headers(client)
    return headers


@pytest.fixture(scope="module")
async def normal_user_token_headers(
    client: AsyncClient, db: AsyncSession
) -> Dict[str, str]:
    headers = await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
    return headers


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
