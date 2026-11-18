from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate, UserRole
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def create_manager(client: TestClient, db: Session) -> tuple[str, dict[str, str]]:
    email = random_email()
    password = random_lower_string()
    crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, role=UserRole.MANAGER),
    )
    headers = user_authentication_headers(client=client, email=email, password=password)
    return email, headers


def test_manager_can_view_users_and_metrics_but_not_change_access(
    client: TestClient, db: Session
) -> None:
    _, manager_headers = create_manager(client, db)

    assert (
        client.get(f"{settings.API_V1_STR}/users/", headers=manager_headers).status_code
        == 200
    )
    assert (
        client.get(
            f"{settings.API_V1_STR}/metrics/", headers=manager_headers
        ).status_code
        == 200
    )
    manager = client.get(
        f"{settings.API_V1_STR}/users/me", headers=manager_headers
    ).json()
    assert (
        client.patch(
            f"{settings.API_V1_STR}/users/{manager['id']}",
            headers=manager_headers,
            json={"role": "admin"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{settings.API_V1_STR}/users/",
            headers=manager_headers,
            json={
                "email": random_email(),
                "password": random_lower_string(),
                "role": "admin",
            },
        ).status_code
        == 403
    )


def test_member_cannot_escalate_role_through_profile_update(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"role": "admin", "is_superuser": True},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "member"
    assert response.json()["is_superuser"] is False
    assert (
        client.get(
            f"{settings.API_V1_STR}/metrics/", headers=normal_user_token_headers
        ).status_code
        == 403
    )


def test_role_and_active_changes_apply_to_existing_sessions(
    client: TestClient,
    db: Session,
    superuser_token_headers: dict[str, str],
) -> None:
    email, manager_headers = create_manager(client, db)
    manager = crud.get_user_by_email(session=db, email=email)
    assert manager

    response = client.patch(
        f"{settings.API_V1_STR}/users/{manager.id}",
        headers=superuser_token_headers,
        json={"role": "member"},
    )
    assert response.status_code == 200
    assert (
        client.get(f"{settings.API_V1_STR}/users/", headers=manager_headers).status_code
        == 403
    )

    response = client.patch(
        f"{settings.API_V1_STR}/users/{manager.id}",
        headers=superuser_token_headers,
        json={"role": "manager", "is_active": False},
    )
    assert response.status_code == 200
    assert (
        client.get(
            f"{settings.API_V1_STR}/users/me", headers=manager_headers
        ).status_code
        == 400
    )
