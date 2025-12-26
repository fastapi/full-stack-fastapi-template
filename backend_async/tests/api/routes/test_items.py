import uuid

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from tests.utils.item import create_random_item

pytestmark = pytest.mark.usefixtures('anyio_backend')

async def test_create_item(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


async def test_read_item(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_read_item_not_found(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    response = await client.get(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_read_item_not_enough_permissions(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_read_items(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    await create_random_item(db)
    await create_random_item(db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


async def test_update_item(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_update_item_not_found(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_update_item_not_enough_permissions(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_delete_item(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


async def test_delete_item_not_found(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    response = await client.delete(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_delete_item_not_enough_permissions(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
