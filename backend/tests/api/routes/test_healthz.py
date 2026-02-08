from fastapi.testclient import TestClient

from app.core.config import settings


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_configured_origin(client: TestClient) -> None:
    response = client.get("/healthz", headers={"Origin": settings.FRONTEND_HOST})
    assert response.headers.get("access-control-allow-origin") == settings.FRONTEND_HOST


def test_cors_blocks_unknown_origin(client: TestClient) -> None:
    response = client.get("/healthz", headers={"Origin": "https://unknown.example"})
    assert "access-control-allow-origin" not in response.headers
