import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.core.rate_limiter.rate_limiter import RateLimiter


@pytest.fixture
def mock_limiter():
    limiter = AsyncMock()
    limiter.allow_request = AsyncMock(return_value=(True, 0))
    return limiter


def test_dependency_allows_request(mock_limiter):
    app = FastAPI()

    @app.get("/test", dependencies=[Depends(RateLimiter(limit=2, window_seconds=5))])
    async def endpoint():
        return {"ok": True}

    app.state.rate_limiter = mock_limiter

    client = TestClient(app)
    resp = client.get("/test")

    assert resp.status_code == 200
    mock_limiter.allow_request.assert_awaited()


def test_dependency_blocks_request(mock_limiter):
    mock_limiter.allow_request.return_value = (False, 10)

    app = FastAPI()

    @app.get("/test", dependencies=[Depends(RateLimiter(limit=2, window_seconds=5))])
    async def endpoint():
        return {"ok": True}

    app.state.rate_limiter = mock_limiter

    client = TestClient(app)
    resp = client.get("/test")

    assert resp.status_code == 429
    assert "10s" in resp.json()["detail"]
