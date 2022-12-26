import pytest

# from fastapi.testclient import TestClient
from httpx import AsyncClient
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.tests.utils.item import create_random_item

pytestmark = pytest.mark.asyncio


async def test_create_item(
        client: AsyncClient, superuser_token_headers: dict, async_get_db: AsyncSession
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        f"{settings.API_V1_STR}/items/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


async def test_read_item(
        client: AsyncClient, superuser_token_headers: dict, async_get_db: AsyncSession
) -> None:
    item = await create_random_item(async_get_db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id
