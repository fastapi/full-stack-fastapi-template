import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserCreate
from tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.usefixtures('anyio_backend')

async def test_get_users_superuser_me(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


async def test_get_users_normal_user_me(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = await client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


async def test_create_user_new_email(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    with (
        patch("app.utils.send_email", return_value=None),
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        username = random_email()
        password = random_lower_string()
        data = {"email": username, "password": password}
        r = await client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        created_user = r.json()
        user = await crud.get_user_by_email(session=db, email=username)
        assert user
        assert user.email == created_user["email"]


async def test_get_existing_user(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


async def test_get_existing_user_current_user(client: AsyncClient, db: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    login_data = {
        "username": username,
        "password": password,
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


async def test_get_existing_user_permissions_error(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}


async def test_create_user_existing_username(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.create_user(session=db, user_create=user_in)
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


async def test_create_user_by_normal_user(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


async def test_retrieve_users(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.create_user(session=db, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    await crud.create_user(session=db, user_create=user_in2)

    r = await client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item


async def test_update_user_me(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    full_name = "Updated Name"
    email = random_email()
    data = {"full_name": full_name, "email": email}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == email
    assert updated_user["full_name"] == full_name

    user_query = select(User).where(User.email == email)
    user_db = (await db.exec(user_query)).first()
    assert user_db
    assert user_db.email == email
    assert user_db.full_name == full_name


async def test_update_password_me(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    new_password = random_lower_string()
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_db = (await db.exec(user_query)).first()
    assert user_db
    assert user_db.email == settings.FIRST_SUPERUSER
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    await db.refresh(user_db)

    assert r.status_code == 200
    assert verify_password(settings.FIRST_SUPERUSER_PASSWORD, user_db.hashed_password)


async def test_update_password_me_incorrect_password(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


async def test_update_user_me_email_exists(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)

    data = {"email": user.email}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


async def test_update_password_me_same_password_error(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert (
        updated_user["detail"] == "New password cannot be the same as the current one"
    )


async def test_register_user(client: AsyncClient, db: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    r = await client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == username
    assert created_user["full_name"] == full_name

    user_query = select(User).where(User.email == username)
    user_db = (await db.exec(user_query)).first()
    assert user_db
    assert user_db.email == username
    assert user_db.full_name == full_name
    assert verify_password(password, user_db.hashed_password)


async def test_register_user_already_exists_error(client: AsyncClient) -> None:
    password = random_lower_string()
    full_name = random_lower_string()
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": password,
        "full_name": full_name,
    }
    r = await client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "The user with this email already exists in the system"


async def test_update_user(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)

    data = {"full_name": "Updated_full_name"}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()

    assert updated_user["full_name"] == "Updated_full_name"

    user_query = select(User).where(User.email == username)
    user_db = (await db.exec(user_query)).first()
    await db.refresh(user_db)
    assert user_db
    assert user_db.full_name == "Updated_full_name"


async def test_update_user_not_exists(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"full_name": "Updated_full_name"}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


async def test_update_user_email_exists(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)
    user_id = user.id # directly accessing user.id in the patch url raises MissingGreenlet Error

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    user2 = await crud.create_user(session=db, user_create=user_in2)

    data = {"email": user2.email}
    r = await client.patch(
        f"{settings.API_V1_STR}/users/{user_id}", # directly accessing user.id here raises MissingGreenlet Error
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


async def test_delete_user_me(client: AsyncClient, db: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    login_data = {
        "username": username,
        "password": password,
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = await client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = (await db.exec(select(User).where(User.id == user_id))).first()
    assert result is None

    user_query = select(User).where(User.id == user_id)
    user_db = (await db.exec(user_query)).first()
    assert user_db is None


async def test_delete_user_me_as_superuser(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


async def test_delete_user_super_user(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = await client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = (await db.exec(select(User).where(User.id == user_id))).first()
    assert result is None


async def test_delete_user_not_found(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.delete(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


async def test_delete_user_current_super_user_error(
    client: AsyncClient, superuser_token_headers: dict[str, str], db: AsyncSession
) -> None:
    super_user = await crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    r = await client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


async def test_delete_user_without_privileges(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db, user_create=user_in)

    r = await client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"
