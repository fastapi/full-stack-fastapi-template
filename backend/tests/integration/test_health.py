"""Integration tests for operational endpoints (/healthz, /readyz, /version).

Uses a minimal FastAPI app with the health router mounted. All external
dependencies (Supabase) are mocked — no running database required.

Run:
  uv run pytest backend/tests/integration/test_health.py -v
"""

import os

# Ensure required env vars are set for config.Settings import.
# setdefault does NOT overwrite existing env vars; values below are
# only used when running tests outside Docker (no .env loaded).
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("CLERK_SECRET_KEY", "test-clerk-key")

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

from app.api.routes.health import router as health_router

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(supabase_mock: MagicMock | None = None) -> FastAPI:
    """Create a minimal FastAPI app with the health router."""
    app = FastAPI()
    app.include_router(health_router)
    if supabase_mock is not None:
        app.state.supabase = supabase_mock
    return app


def _healthy_supabase() -> MagicMock:
    """Return a mock Supabase client that reports healthy."""
    mock = MagicMock()
    mock.table.return_value.select.return_value.execute.return_value = MagicMock()
    return mock


def _unreachable_supabase() -> MagicMock:
    """Return a mock Supabase client that simulates connection failure."""
    mock = MagicMock()
    mock.table.side_effect = ConnectionError("Connection refused")
    return mock


def _api_error_supabase() -> MagicMock:
    """Return a mock Supabase client where table doesn't exist (PostgREST APIError).

    This simulates the table not existing, but the server being reachable.
    """
    mock = MagicMock()
    mock.table.return_value.select.return_value.execute.side_effect = APIError(
        {"message": "relation '_health_check' does not exist", "code": "PGRST204"}
    )
    return mock


# ---------------------------------------------------------------------------
# /healthz — Liveness probe
# ---------------------------------------------------------------------------


class TestHealthz:
    """Liveness probe tests."""

    def test_returns_200_ok(self) -> None:
        """GET /healthz returns 200 with {"status": "ok"}."""
        client = TestClient(_make_app())

        response = client.get("/healthz")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_no_auth_required(self) -> None:
        """GET /healthz succeeds without Authorization header."""
        client = TestClient(_make_app())

        response = client.get("/healthz", headers={})

        assert response.status_code == 200

    def test_response_schema_exact(self) -> None:
        """Response contains only the 'status' field — no extra keys."""
        client = TestClient(_make_app())

        data = client.get("/healthz").json()

        assert set(data.keys()) == {"status"}

    def test_never_checks_dependencies(self) -> None:
        """Healthz does not access app.state.supabase (liveness only)."""
        mock = MagicMock()
        client = TestClient(_make_app(supabase_mock=mock))

        client.get("/healthz")

        mock.table.assert_not_called()


# ---------------------------------------------------------------------------
# /readyz — Readiness probe
# ---------------------------------------------------------------------------


class TestReadyz:
    """Readiness probe tests."""

    def test_healthy_supabase_returns_200(self) -> None:
        """GET /readyz returns 200 when Supabase is reachable."""
        client = TestClient(_make_app(supabase_mock=_healthy_supabase()))

        response = client.get("/readyz")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ready",
            "checks": {"supabase": "ok"},
        }

    def test_unreachable_supabase_returns_503(self) -> None:
        """GET /readyz returns 503 when Supabase is unreachable."""
        client = TestClient(_make_app(supabase_mock=_unreachable_supabase()))

        response = client.get("/readyz")

        assert response.status_code == 503
        assert response.json() == {
            "status": "not_ready",
            "checks": {"supabase": "error"},
        }

    def test_api_error_still_reports_ok(self) -> None:
        """PostgREST APIError (table not found) means server IS reachable."""
        client = TestClient(_make_app(supabase_mock=_api_error_supabase()))

        response = client.get("/readyz")

        assert response.status_code == 200
        assert response.json()["checks"]["supabase"] == "ok"

    def test_missing_supabase_client_returns_503(self) -> None:
        """GET /readyz returns 503 when app.state.supabase is not set."""
        client = TestClient(_make_app())  # No supabase mock set

        response = client.get("/readyz")

        assert response.status_code == 503
        assert response.json()["checks"]["supabase"] == "error"

    def test_exception_does_not_crash(self) -> None:
        """Supabase check exception returns valid JSON, not a 500 crash."""
        mock = MagicMock()
        mock.table.side_effect = RuntimeError("unexpected")
        client = TestClient(_make_app(supabase_mock=mock))

        response = client.get("/readyz")

        assert response.status_code == 503
        assert response.headers["content-type"] == "application/json"
        body = response.json()
        assert body["status"] == "not_ready"
        assert body["checks"]["supabase"] == "error"

    def test_no_auth_required(self) -> None:
        """GET /readyz succeeds without Authorization header."""
        client = TestClient(_make_app(supabase_mock=_healthy_supabase()))

        response = client.get("/readyz", headers={})

        assert response.status_code == 200

    def test_response_schema_exact(self) -> None:
        """Response contains only 'status' and 'checks' — no extra keys."""
        client = TestClient(_make_app(supabase_mock=_healthy_supabase()))

        data = client.get("/readyz").json()

        assert set(data.keys()) == {"status", "checks"}
        assert set(data["checks"].keys()) == {"supabase"}


# ---------------------------------------------------------------------------
# /version — Build metadata
# ---------------------------------------------------------------------------


class TestVersion:
    """Build metadata endpoint tests."""

    def test_returns_200_with_metadata(self) -> None:
        """GET /version returns 200 with all required metadata fields."""
        client = TestClient(_make_app())

        response = client.get("/version")

        assert response.status_code == 200
        data = response.json()
        assert "service_name" in data
        assert "version" in data
        assert "commit" in data
        assert "build_time" in data
        assert "environment" in data

    def test_includes_service_name(self) -> None:
        """GET /version includes service_name for gateway discoverability."""
        mock_settings = MagicMock()
        mock_settings.SERVICE_NAME = "my-service"
        mock_settings.SERVICE_VERSION = "0.1.0"
        mock_settings.GIT_COMMIT = "unknown"
        mock_settings.BUILD_TIME = "unknown"
        mock_settings.ENVIRONMENT = "local"

        with patch("app.api.routes.health.settings", mock_settings):
            data = TestClient(_make_app()).get("/version").json()

        assert data["service_name"] == "my-service"

    def test_default_values_for_unset_env_vars(self) -> None:
        """GIT_COMMIT and BUILD_TIME default to 'unknown' when not set."""
        mock_settings = MagicMock()
        mock_settings.SERVICE_NAME = "my-service"
        mock_settings.SERVICE_VERSION = "0.1.0"
        mock_settings.GIT_COMMIT = "unknown"
        mock_settings.BUILD_TIME = "unknown"
        mock_settings.ENVIRONMENT = "local"

        with patch("app.api.routes.health.settings", mock_settings):
            data = TestClient(_make_app()).get("/version").json()

        assert data["commit"] == "unknown"
        assert data["build_time"] == "unknown"

    def test_custom_settings_values(self) -> None:
        """Version endpoint reflects custom settings values."""
        mock_settings = MagicMock()
        mock_settings.SERVICE_NAME = "custom-service"
        mock_settings.SERVICE_VERSION = "2.0.0"
        mock_settings.GIT_COMMIT = "abc1234"
        mock_settings.BUILD_TIME = "2026-02-28T00:00:00Z"
        mock_settings.ENVIRONMENT = "staging"

        with patch("app.api.routes.health.settings", mock_settings):
            client = TestClient(_make_app())
            data = client.get("/version").json()

        assert data == {
            "service_name": "custom-service",
            "version": "2.0.0",
            "commit": "abc1234",
            "build_time": "2026-02-28T00:00:00Z",
            "environment": "staging",
        }

    def test_response_schema_exact(self) -> None:
        """Response contains exactly the five expected fields."""
        client = TestClient(_make_app())

        data = client.get("/version").json()

        assert set(data.keys()) == {
            "service_name",
            "version",
            "commit",
            "build_time",
            "environment",
        }

    def test_no_auth_required(self) -> None:
        """GET /version succeeds without Authorization header."""
        client = TestClient(_make_app())

        response = client.get("/version", headers={})

        assert response.status_code == 200
