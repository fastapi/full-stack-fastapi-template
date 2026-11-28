from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserRole
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user, user_authentication_headers
from tests.utils.utils import random_email, random_lower_string

API = settings.API_V1_STR


def _user_with_headers(
    client: TestClient, db: Session, role: UserRole
) -> tuple[User, dict[str, str]]:
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password, role=role)
    )
    headers = user_authentication_headers(client=client, email=email, password=password)
    return user, headers


def test_manager_can_read_users_and_metrics(client: TestClient, db: Session) -> None:
    _, headers = _user_with_headers(client, db, UserRole.MANAGER)
    other = create_random_user(db)

    assert client.get(f"{API}/users/", headers=headers).status_code == 200
    r = client.get(f"{API}/users/{other.id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == other.email
    r = client.get(f"{API}/metrics/", headers=headers)
    assert r.status_code == 200
    assert set(r.json()) == {"total_users", "active_users", "total_items"}


def test_manager_cannot_mutate_users(client: TestClient, db: Session) -> None:
    _, headers = _user_with_headers(client, db, UserRole.MANAGER)
    other = create_random_user(db)

    create = client.post(
        f"{API}/users/",
        headers=headers,
        json={"email": random_email(), "password": random_lower_string()},
    )
    update = client.patch(
        f"{API}/users/{other.id}", headers=headers, json={"role": "admin"}
    )
    delete = client.delete(f"{API}/users/{other.id}", headers=headers)
    test_email = client.post(
        f"{API}/utils/test-email/", headers=headers, params={"email_to": other.email}
    )
    recovery_html = client.post(
        f"{API}/password-recovery-html-content/{other.email}", headers=headers
    )

    for r in (create, update, delete, test_email, recovery_html):
        assert r.status_code == 403
    db.refresh(other)
    assert other.role == UserRole.MEMBER


def test_member_blocked_from_staff_endpoints(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other = create_random_user(db)

    assert (
        client.get(f"{API}/users/", headers=normal_user_token_headers).status_code
        == 403
    )
    assert (
        client.get(f"{API}/metrics/", headers=normal_user_token_headers).status_code
        == 403
    )
    assert (
        client.get(
            f"{API}/users/{other.id}", headers=normal_user_token_headers
        ).status_code
        == 403
    )


def test_member_cannot_probe_user_ids(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{API}/users/00000000-0000-0000-0000-000000000000",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_signup_ignores_role_and_is_active(client: TestClient) -> None:
    r = client.post(
        f"{API}/users/signup",
        json={
            "email": random_email(),
            "password": random_lower_string(),
            "role": "admin",
            "is_active": False,
        },
    )
    assert r.status_code == 200
    assert r.json()["role"] == "member"
    assert r.json()["is_active"] is True


def test_update_me_ignores_role(client: TestClient, db: Session) -> None:
    user, headers = _user_with_headers(client, db, UserRole.MEMBER)

    r = client.patch(
        f"{API}/users/me", headers=headers, json={"role": "admin", "full_name": "X"}
    )

    assert r.status_code == 200
    assert r.json()["role"] == "member"
    db.refresh(user)
    assert user.role == UserRole.MEMBER


def test_admin_rejects_invalid_role(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{API}/users/",
        headers=superuser_token_headers,
        json={
            "email": random_email(),
            "password": random_lower_string(),
            "role": "owner",
        },
    )
    assert r.status_code == 422


def test_admin_cannot_demote_or_deactivate_self(
    client: TestClient, db: Session
) -> None:
    admin, headers = _user_with_headers(client, db, UserRole.ADMIN)

    demote = client.patch(
        f"{API}/users/{admin.id}", headers=headers, json={"role": "manager"}
    )
    deactivate = client.patch(
        f"{API}/users/{admin.id}", headers=headers, json={"is_active": False}
    )
    rename = client.patch(
        f"{API}/users/{admin.id}",
        headers=headers,
        json={"full_name": "Still Admin", "role": "admin", "is_active": True},
    )

    assert demote.status_code == 403
    assert deactivate.status_code == 403
    assert rename.status_code == 200
    db.refresh(admin)
    assert admin.role == UserRole.ADMIN
    assert admin.is_active is True
    assert admin.full_name == "Still Admin"


def test_role_changes_apply_to_existing_token(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user, headers = _user_with_headers(client, db, UserRole.MEMBER)
    assert client.get(f"{API}/users/", headers=headers).status_code == 403

    client.patch(
        f"{API}/users/{user.id}",
        headers=superuser_token_headers,
        json={"role": "manager"},
    )
    assert client.get(f"{API}/users/", headers=headers).status_code == 200

    client.patch(
        f"{API}/users/{user.id}",
        headers=superuser_token_headers,
        json={"role": "member"},
    )
    assert client.get(f"{API}/users/", headers=headers).status_code == 403


def test_deactivation_applies_to_existing_token(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user, headers = _user_with_headers(client, db, UserRole.MANAGER)
    assert client.get(f"{API}/users/me", headers=headers).status_code == 200

    client.patch(
        f"{API}/users/{user.id}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )

    r = client.get(f"{API}/users/me", headers=headers)
    assert r.status_code == 400
    assert r.json()["detail"] == "Inactive user"


def test_manager_cannot_access_others_items(client: TestClient, db: Session) -> None:
    _, headers = _user_with_headers(client, db, UserRole.MANAGER)
    item = create_random_item(db)

    assert client.get(f"{API}/items/{item.id}", headers=headers).status_code == 403
    assert (
        client.put(
            f"{API}/items/{item.id}", headers=headers, json={"title": "hijack"}
        ).status_code
        == 403
    )
    assert client.delete(f"{API}/items/{item.id}", headers=headers).status_code == 403
    r = client.get(f"{API}/items/", headers=headers)
    assert r.json()["count"] == 0
