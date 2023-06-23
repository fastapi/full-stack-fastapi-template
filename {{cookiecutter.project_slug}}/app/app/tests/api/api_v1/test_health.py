import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_health(
    client: AsyncClient
) -> None:
    response = await client.get(
        f"{settings.API_V1_STR}/_health",
    )
    assert response.status_code == 200
    content = response.json()
    assert content == "OK"