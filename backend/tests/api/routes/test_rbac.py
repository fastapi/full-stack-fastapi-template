"""Focused coverage of the role/permission matrix documented in docs/AUTHORIZATION.md.

One allowed and one denied case per permission, plus the privilege-escalation
check on self-update — not an exhaustive role x permission grid.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import User
from tests.utils.user import create_random_user


def test_manager_can_list_users(
    client: TestClient, manager_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=manager_user_token_headers)
    assert r.status_code == 200


def test_member_cannot_list_users(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_manager_cannot_create_user(
    client: TestClient, manager_user_token_headers: dict[str, str]
) -> None:
    data = {"email": "new-user@example.com", "password": "password123"}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=manager_user_token_headers, json=data
    )
    assert r.status_code == 403


def test_manager_can_view_metrics(
    client: TestClient, manager_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/metrics/", headers=manager_user_token_headers
    )
    assert r.status_code == 200
    assert "user_count" in r.json()


def test_member_cannot_view_metrics(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_manager_cannot_update_another_user(
    client: TestClient, manager_user_token_headers: dict[str, str], db: Session
) -> None:
    other_user = create_random_user(db)
    r = client.patch(
        f"{settings.API_V1_STR}/users/{other_user.id}",
        headers=manager_user_token_headers,
        json={"full_name": "Renamed"},
    )
    assert r.status_code == 403


def test_member_cannot_escalate_role_via_self_update(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"full_name": "Still Member", "role": "admin"},
    )
    assert r.status_code == 200

    user = db.exec(select(User).where(User.email == settings.EMAIL_TEST_USER)).first()
    assert user
    assert user.role.slug == "member"
