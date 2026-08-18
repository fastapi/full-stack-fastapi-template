# Backend authorization tests for admin, manager, and member roles.
import logging

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.user import (
    authentication_token_from_email,
    user_authentication_headers,
)


def test_manager_can_list_users(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    response = client.get(f"{settings.API_V1_STR}/users/", headers=manager_token_headers)
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


def test_member_cannot_update_other_users(
    client: TestClient,
    member_token_headers: dict[str, str],
    db: Session,
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
