# Backend authorization tests for admin, manager, and member roles.
import logging

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate, UserUpdate
from tests.utils.item import create_random_item
from tests.utils.user import (
    user_authentication_headers,
)
from tests.utils.utils import random_email, random_lower_string


def test_manager_can_list_users(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=manager_token_headers
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_manager_cannot_create_user(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=manager_token_headers,
        json={
            "email": "new-manager-blocked@example.com",
            "password": "securepass1",
        },
    )
    assert response.status_code == 403


def test_member_cannot_list_users(
    client: TestClient, member_token_headers: dict[str, str]
) -> None:
    response = client.get(f"{settings.API_V1_STR}/users/", headers=member_token_headers)
    assert response.status_code == 403


def test_permission_denial_is_logged(
    client: TestClient,
    member_token_headers: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.api.deps"):
        response = client.get(
            f"{settings.API_V1_STR}/users/", headers=member_token_headers
        )

    assert response.status_code == 403
    assert "Access denied" in caplog.text
    assert "users:list" in caplog.text


def test_member_can_update_own_profile(
    client: TestClient, member_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=member_token_headers,
        json={"full_name": "Member Updated"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Member Updated"


def test_admin_can_create_user(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json={
            "email": "rbac-admin-created@example.com",
            "password": "securepass1",
            "role": "member",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "rbac-admin-created@example.com"


def test_metrics_admin_and_manager_allowed_member_denied(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    manager_token_headers: dict[str, str],
    member_token_headers: dict[str, str],
) -> None:
    admin_response = client.get(
        f"{settings.API_V1_STR}/metrics/", headers=superuser_token_headers
    )
    manager_response = client.get(
        f"{settings.API_V1_STR}/metrics/", headers=manager_token_headers
    )
    member_response = client.get(
        f"{settings.API_V1_STR}/metrics/", headers=member_token_headers
    )

    assert admin_response.status_code == 200
    assert manager_response.status_code == 200
    assert member_response.status_code == 403


def test_manager_cannot_access_other_users_item(
    client: TestClient, manager_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=manager_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_invalid_access_token(client: TestClient) -> None:
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Could not validate credentials"


def test_inactive_user_cannot_access(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=True)
    user = crud.create_user(session=db, user_create=user_in)
    headers = user_authentication_headers(client=client, email=email, password=password)

    user_in_update = UserUpdate(is_active=False)
    crud.update_user(session=db, db_user=user, user_in=user_in_update)

    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


def test_token_for_deleted_user_returns_not_found(
    client: TestClient, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    headers = user_authentication_headers(client=client, email=email, password=password)
    db.delete(user)
    db.commit()

    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_non_admin_cannot_access_superuser_utils_endpoint(
    client: TestClient,
    member_token_headers: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.api.deps"):
        response = client.post(
            f"{settings.API_V1_STR}/utils/test-email/?email_to=member@example.com",
            headers=member_token_headers,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"
    assert "Access denied" in caplog.text
    assert "admin" in caplog.text.lower()


def test_member_cannot_update_other_users(
    client: TestClient,
    member_token_headers: dict[str, str],
) -> None:
    admin_headers = user_authentication_headers(
        client=client,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
    )
    admin_me = client.get(
        f"{settings.API_V1_STR}/users/me", headers=admin_headers
    ).json()

    response = client.patch(
        f"{settings.API_V1_STR}/users/{admin_me['id']}",
        headers=member_token_headers,
        json={"full_name": "Escalation Attempt"},
    )
    assert response.status_code == 403
