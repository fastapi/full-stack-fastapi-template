from typing import Dict
import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_celery_worker_test(
        client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"msg": "test"}
    r = await client.post(
        f"{settings.API_V1_STR}/utils/test-celery/",
        json=data,
        headers=superuser_token_headers,
    )
    response = r.json()
    assert response["msg"] == "Word received"
