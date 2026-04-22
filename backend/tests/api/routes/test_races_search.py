"""Tests for search & discovery race endpoints."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Race, RaceStatusEnum

API = settings.API_V1_STR


def _create_race(
    client: TestClient,
    headers: dict[str, str],
    name: str = "Test Race",
    status: str = "published",
    **kwargs: object,
) -> dict:
    payload = {
        "name": name,
        "status": status,
        "city": "Hanoi",
        "country": "Vietnam",
        **kwargs,
    }
    r = client.post(f"{API}/races/", headers=headers, json=payload)
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# /search
# ---------------------------------------------------------------------------


def test_search_races_empty_query(client: TestClient) -> None:
    r = client.get(f"{API}/races/search")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body


def test_search_races_with_q(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    slug = uuid.uuid4().hex[:8]
    _create_race(client, superuser_token_headers, name=f"UniqueMarathon {slug}")
    r = client.get(f"{API}/races/search", params={"q": f"UniqueMarathon {slug}"})
    assert r.status_code == 200


def test_search_races_status_filter(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    _create_race(client, superuser_token_headers, status="draft")
    r = client.get(f"{API}/races/search", params={"status": "published"})
    assert r.status_code == 200
    body = r.json()
    for race in body["data"]:
        assert race["status"] == "published"


def test_search_races_terrain_filter(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    _create_race(
        client, superuser_token_headers, name="Trail Blast", terrain_type="trail"
    )
    r = client.get(f"{API}/races/search", params={"terrain": "trail"})
    assert r.status_code == 200
    body = r.json()
    for race in body["data"]:
        assert race["terrain_type"] == "trail"


def test_search_races_sort_options(client: TestClient) -> None:
    for sort in ("date", "popularity"):
        r = client.get(f"{API}/races/search", params={"sort": sort})
        assert r.status_code == 200

    r = client.get(f"{API}/races/search", params={"sort": "invalid"})
    assert r.status_code == 422


def test_search_races_pagination(client: TestClient) -> None:
    r = client.get(f"{API}/races/search", params={"skip": 0, "limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert len(body["data"]) <= 5


# ---------------------------------------------------------------------------
# /nearby
# ---------------------------------------------------------------------------


def test_nearby_requires_lat_lon(client: TestClient) -> None:
    r = client.get(f"{API}/races/nearby")
    assert r.status_code == 422


def test_nearby_returns_list(client: TestClient) -> None:
    r = client.get(
        f"{API}/races/nearby", params={"lat": 21.03, "lon": 105.83, "radius_km": 500}
    )
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body
    for race in body["data"]:
        assert "distance_km" in race


def test_nearby_distance_is_numeric(client: TestClient) -> None:
    r = client.get(
        f"{API}/races/nearby",
        params={"lat": 0, "lon": 0, "radius_km": 20000},
    )
    assert r.status_code == 200
    for race in r.json()["data"]:
        assert isinstance(race["distance_km"], float)


# ---------------------------------------------------------------------------
# /trending
# ---------------------------------------------------------------------------


def test_trending_public(client: TestClient) -> None:
    r = client.get(f"{API}/races/trending")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body


def test_trending_days_param(client: TestClient) -> None:
    r = client.get(f"{API}/races/trending", params={"days": 30, "limit": 5})
    assert r.status_code == 200


def test_trending_invalid_days(client: TestClient) -> None:
    r = client.get(f"{API}/races/trending", params={"days": 0})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# /recommended
# ---------------------------------------------------------------------------


def test_recommended_requires_auth(client: TestClient) -> None:
    r = client.get(f"{API}/races/recommended")
    assert r.status_code == 403


def test_recommended_for_authenticated_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{API}/races/recommended", headers=normal_user_token_headers)
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body


def test_recommended_with_profile(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    # Create a profile to get non-fallback recommendations
    client.post(
        f"{API}/users/me/profile",
        headers=normal_user_token_headers,
        json={"fitness_level": "intermediate", "terrain_preference": "trail"},
    )
    r = client.get(f"{API}/races/recommended", headers=normal_user_token_headers)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# /{race_id}/similar
# ---------------------------------------------------------------------------


def test_similar_not_found(client: TestClient) -> None:
    r = client.get(f"{API}/races/{uuid.uuid4()}/similar")
    assert r.status_code == 404


def test_similar_returns_list(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    race = _create_race(
        client, superuser_token_headers, name="Base Race", terrain_type="road"
    )
    r = client.get(f"{API}/races/{race['id']}/similar")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    for r_item in body["data"]:
        assert r_item["id"] != race["id"]
