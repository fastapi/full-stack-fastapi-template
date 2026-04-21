"""API tests for /users/me/profile and saved-race endpoints."""

from fastapi.testclient import TestClient

from app.core.config import settings


API = settings.API_V1_STR


# ---------------------------------------------------------------------------
# Profile endpoints
# ---------------------------------------------------------------------------


def test_get_profile_unauthenticated(client: TestClient) -> None:
    r = client.get(f"{API}/users/me/profile")
    assert r.status_code == 403


def test_get_profile_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{API}/users/me/profile", headers=normal_user_token_headers)
    # Profile doesn't exist yet for a fresh user
    assert r.status_code == 404


def test_create_profile(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {
        "fitness_level": "intermediate",
        "distance_preference": "mid",
        "terrain_preference": "trail",
        "home_city": "Hanoi",
        "is_onboarded": True,
    }
    r = client.post(
        f"{API}/users/me/profile", headers=normal_user_token_headers, json=data
    )
    assert r.status_code == 200
    body = r.json()
    assert body["fitness_level"] == "intermediate"
    assert body["terrain_preference"] == "trail"
    assert body["home_city"] == "Hanoi"
    assert body["is_onboarded"] is True
    assert "id" in body
    assert "user_id" in body


def test_get_profile_after_create(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    # Ensure profile exists
    client.post(
        f"{API}/users/me/profile",
        headers=normal_user_token_headers,
        json={"fitness_level": "beginner", "is_onboarded": False},
    )
    r = client.get(f"{API}/users/me/profile", headers=normal_user_token_headers)
    assert r.status_code == 200
    body = r.json()
    assert "fitness_level" in body


def test_patch_profile(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    # Ensure profile exists
    client.post(
        f"{API}/users/me/profile",
        headers=normal_user_token_headers,
        json={"fitness_level": "beginner"},
    )
    r = client.patch(
        f"{API}/users/me/profile",
        headers=normal_user_token_headers,
        json={"home_city": "Da Nang"},
    )
    assert r.status_code == 200
    assert r.json()["home_city"] == "Da Nang"


def test_upsert_profile_is_idempotent(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"fitness_level": "elite", "is_onboarded": True}
    r1 = client.post(
        f"{API}/users/me/profile", headers=normal_user_token_headers, json=data
    )
    r2 = client.post(
        f"{API}/users/me/profile", headers=normal_user_token_headers, json=data
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_delete_profile(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Create then delete as superuser
    client.post(
        f"{API}/users/me/profile",
        headers=superuser_token_headers,
        json={"is_onboarded": True},
    )
    r = client.delete(f"{API}/users/me/profile", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Profile deleted"


# ---------------------------------------------------------------------------
# Saved races
# ---------------------------------------------------------------------------


def test_get_saved_races_empty(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{API}/users/me/saved-races", headers=normal_user_token_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["data"] == []
    assert body["count"] == 0


def test_save_race_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    import uuid
    r = client.post(
        f"{API}/races/{uuid.uuid4()}/save", headers=normal_user_token_headers
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


def test_list_tags_public(client: TestClient) -> None:
    r = client.get(f"{API}/tags/")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body


def test_create_tag_requires_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{API}/tags/",
        headers=normal_user_token_headers,
        json={"name": "Scenic", "slug": "scenic"},
    )
    assert r.status_code == 403


def test_create_tag_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    import uuid
    slug = f"test-{uuid.uuid4().hex[:8]}"
    r = client.post(
        f"{API}/tags/",
        headers=superuser_token_headers,
        json={"name": f"Tag {slug}", "slug": slug},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == slug
    assert "id" in body


def test_create_duplicate_tag_returns_409(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    import uuid
    slug = f"dup-{uuid.uuid4().hex[:8]}"
    client.post(
        f"{API}/tags/",
        headers=superuser_token_headers,
        json={"name": f"Dup {slug}", "slug": slug},
    )
    r = client.post(
        f"{API}/tags/",
        headers=superuser_token_headers,
        json={"name": f"Dup2 {slug}", "slug": slug},
    )
    assert r.status_code == 409
