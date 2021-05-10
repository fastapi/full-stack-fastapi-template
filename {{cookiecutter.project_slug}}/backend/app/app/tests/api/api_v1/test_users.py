from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate
from app.tests.utils.utils import random_email, random_lower_string


pytestmark = pytest.mark.asyncio


async def test_get_users_superuser_me(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


async def test_get_users_normal_user_me(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


async def test_create_user_new_email(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = await crud.user.get_by_email(db, email=username)
    assert user
    assert user.email == created_user["email"]


async def test_get_existing_user(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.user.get_by_email(db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


async def test_create_user_existing_username(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    username = random_email()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.user.create(db, obj_in=user_in)
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


async def test_create_user_by_normal_user(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers, json=data,
    )
    assert r.status_code == 400


async def test_retrieve_users(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.user.create(db, obj_in=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    await crud.user.create(db, obj_in=user_in2)

    r = await client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item
