"""Unit tests for the Supabase client initialization module.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/supabase.py

Uses unittest.mock to patch supabase.create_client and a minimal FastAPI app
to test the get_supabase dependency — does NOT import the real app from
main.py, so no DB or config fixtures are required.

Run with:
  uv run pytest backend/tests/unit/test_supabase.py -v
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.errors import register_exception_handlers
from app.core.supabase import create_supabase_client, get_supabase

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_app() -> FastAPI:
    """Minimal FastAPI app with error handlers and a get_supabase endpoint."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test-supabase")
    def test_endpoint(_supabase_client=Depends(get_supabase)):
        return {"ok": True}

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app, raise_server_exceptions=False)


@pytest.fixture
def client_with_state(test_app: FastAPI) -> TestClient:
    """TestClient whose app.state.supabase is set to a mock client."""
    mock_supabase = MagicMock()
    test_app.state.supabase = mock_supabase
    return TestClient(test_app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# create_supabase_client tests
# ---------------------------------------------------------------------------


def test_create_supabase_client_returns_client():
    """create_supabase_client calls supabase.create_client with url and key
    and returns the resulting Client instance."""
    mock_client = MagicMock()

    with patch(
        "app.core.supabase.supabase.create_client", return_value=mock_client
    ) as mock_fn:
        result = create_supabase_client(
            url="https://test.supabase.co",
            key="test-service-key",
        )

    mock_fn.assert_called_once_with("https://test.supabase.co", "test-service-key")
    assert result is mock_client


def test_create_supabase_client_failure_raises_service_error():
    """When supabase.create_client raises any exception, create_supabase_client
    wraps it in a ServiceError with status_code=503."""
    from app.core.errors import ServiceError

    with patch(
        "app.core.supabase.supabase.create_client",
        side_effect=Exception("connection refused"),
    ):
        with pytest.raises(ServiceError) as exc_info:
            create_supabase_client(
                url="https://bad.supabase.co",
                key="invalid-key",
            )

    err = exc_info.value
    assert err.status_code == 503
    assert err.code == "SERVICE_UNAVAILABLE"


# ---------------------------------------------------------------------------
# get_supabase dependency tests
# ---------------------------------------------------------------------------


def test_get_supabase_returns_from_app_state(client_with_state: TestClient):
    """When app.state.supabase is set, GET /test-supabase returns 200 ok."""
    response = client_with_state.get("/test-supabase")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_get_supabase_missing_state_raises_503(client: TestClient):
    """When app.state.supabase is NOT set, GET /test-supabase returns 503."""
    response = client.get("/test-supabase")
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "SERVICE_UNAVAILABLE"
    assert body["code"] == "SERVICE_UNAVAILABLE"
