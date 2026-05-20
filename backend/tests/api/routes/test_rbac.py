from fastapi.testclient import TestClient

from app.core.config import settings


def test_admin_can_list_users(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    assert "data" in r.json()


def test_manager_can_list_users(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=manager_token_headers)
    assert 200 <= r.status_code < 300


def test_member_cannot_list_users(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_manager_cannot_create_user(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=manager_token_headers,
        json={"email": "new@example.com", "password": "longenoughpassword"},
    )
    assert r.status_code == 403


def test_member_can_read_own_profile(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert 200 <= r.status_code < 300
    assert "role" in current_user


def test_member_cannot_view_metrics(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_manager_can_view_metrics(
    client: TestClient, manager_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=manager_token_headers)
    assert 200 <= r.status_code < 300


def test_unauthenticated_cannot_list_users(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/")
    assert r.status_code == 401
