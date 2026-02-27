"""Unit tests for the request pipeline middleware.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/middleware.py

Uses a minimal FastAPI app with the middleware registered — does NOT import
the real app from main.py, so no DB or config fixtures are required.
Run with:
  uv run pytest backend/tests/unit/test_middleware.py -v
"""

import io
import json
import uuid

import pytest
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.core.middleware import RequestPipelineMiddleware

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal settings-like object."""

    class _FakeSettings:
        LOG_LEVEL: str = overrides.get("LOG_LEVEL", "DEBUG")
        LOG_FORMAT: str = overrides.get("LOG_FORMAT", "json")
        SERVICE_NAME: str = overrides.get("SERVICE_NAME", "test-svc")
        SERVICE_VERSION: str = overrides.get("SERVICE_VERSION", "0.0.1")
        ENVIRONMENT: str = overrides.get("ENVIRONMENT", "local")

    return _FakeSettings()


def _is_valid_uuid4(value: str) -> bool:
    """Return True if value is a valid UUID string."""
    try:
        parsed = uuid.UUID(value)
        return parsed.version == 4
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _setup_structlog():
    """Ensure structlog is configured before each test."""
    setup_logging(_make_settings())


@pytest.fixture
def app_local() -> FastAPI:
    """FastAPI app with middleware, ENVIRONMENT=local."""
    app = FastAPI()
    app.add_middleware(RequestPipelineMiddleware, environment="local")

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/not-found")
    async def not_found():
        return JSONResponse(status_code=404, content={"error": "not found"})

    @app.get("/server-error")
    async def server_error():
        return JSONResponse(status_code=500, content={"error": "boom"})

    @app.get("/unhandled")
    async def unhandled():
        raise RuntimeError("unexpected crash")

    @app.get("/authenticated")
    async def authenticated(request: Request):
        request.state.user_id = "user-42"
        return {"user": "user-42"}

    return app


@pytest.fixture
def client(app_local: FastAPI) -> TestClient:
    return TestClient(app_local, raise_server_exceptions=False)


@pytest.fixture
def app_production() -> FastAPI:
    """FastAPI app with middleware, ENVIRONMENT=production."""
    app = FastAPI()
    app.add_middleware(RequestPipelineMiddleware, environment="production")

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    return app


@pytest.fixture
def client_production(app_production: FastAPI) -> TestClient:
    return TestClient(app_production, raise_server_exceptions=False)


@pytest.fixture
def app_with_cors() -> FastAPI:
    """FastAPI app with CORS + RequestPipelineMiddleware to test ordering.

    Middleware ordering in Starlette: last-added = outermost.
    CORSMiddleware is added first (inner), RequestPipelineMiddleware second
    (outer). This means our middleware wraps CORS, so even preflight OPTIONS
    responses get security headers and X-Request-ID.
    """
    app = FastAPI()
    # Inner: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://example.com"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Outer: our pipeline middleware
    app.add_middleware(RequestPipelineMiddleware, environment="local")

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    return app


@pytest.fixture
def client_cors(app_with_cors: FastAPI) -> TestClient:
    return TestClient(app_with_cors, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Request ID tests
# ---------------------------------------------------------------------------


def test_request_id_generated_uuid4(client: TestClient):
    """Response has X-Request-ID header with valid UUID v4."""
    response = client.get("/ok")
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert _is_valid_uuid4(request_id)


def test_request_id_unique_per_request(client: TestClient):
    """Two requests get different request_ids."""
    r1 = client.get("/ok")
    r2 = client.get("/ok")
    assert r1.headers["x-request-id"] != r2.headers["x-request-id"]


def test_request_id_in_request_state(app_local: FastAPI):
    """request.state.request_id is set and accessible to handlers."""
    captured_id: str | None = None

    @app_local.get("/capture-state")
    async def capture(request: Request):
        nonlocal captured_id
        captured_id = getattr(request.state, "request_id", None)
        return {"ok": True}

    with TestClient(app_local, raise_server_exceptions=False) as c:
        response = c.get("/capture-state")
    assert response.status_code == 200
    assert captured_id is not None
    assert _is_valid_uuid4(captured_id)


# ---------------------------------------------------------------------------
# Correlation ID tests
# ---------------------------------------------------------------------------


def test_correlation_id_propagated_from_header(client: TestClient):
    """Incoming X-Correlation-ID is preserved, not regenerated."""
    response = client.get("/ok", headers={"X-Correlation-ID": "trace-abc-123"})
    assert response.status_code == 200
    # Verify via request state: the correlation_id in the response log should match
    # We check indirectly that the header didn't replace it:
    # the X-Request-ID should be a NEW uuid, not "trace-abc-123"
    request_id = response.headers["x-request-id"]
    assert request_id != "trace-abc-123"


def test_correlation_id_in_request_state(app_local: FastAPI):
    """correlation_id from X-Correlation-ID header is stored in request.state."""
    captured_corr: str | None = None

    @app_local.get("/capture-corr")
    async def capture(request: Request):
        nonlocal captured_corr
        captured_corr = getattr(request.state, "correlation_id", None)
        return {"ok": True}

    with TestClient(app_local, raise_server_exceptions=False) as c:
        c.get("/capture-corr", headers={"X-Correlation-ID": "trace-xyz"})
    assert captured_corr == "trace-xyz"


def test_correlation_id_fallback_to_request_id(app_local: FastAPI):
    """No X-Correlation-ID header → request_id used as correlation_id."""
    captured_req_id: str | None = None
    captured_corr_id: str | None = None

    @app_local.get("/capture-both")
    async def capture(request: Request):
        nonlocal captured_req_id, captured_corr_id
        captured_req_id = getattr(request.state, "request_id", None)
        captured_corr_id = getattr(request.state, "correlation_id", None)
        return {"ok": True}

    with TestClient(app_local, raise_server_exceptions=False) as c:
        c.get("/capture-both")
    assert captured_req_id is not None
    assert captured_corr_id is not None
    assert captured_req_id == captured_corr_id


# ---------------------------------------------------------------------------
# Security header tests
# ---------------------------------------------------------------------------


def test_security_header_x_content_type_options(client: TestClient):
    """X-Content-Type-Options: nosniff on every response."""
    response = client.get("/ok")
    assert response.headers["x-content-type-options"] == "nosniff"


def test_security_header_x_frame_options(client: TestClient):
    """X-Frame-Options: DENY on every response."""
    response = client.get("/ok")
    assert response.headers["x-frame-options"] == "DENY"


def test_security_header_x_xss_protection(client: TestClient):
    """X-XSS-Protection: 0 (disabled, CSP preferred)."""
    response = client.get("/ok")
    assert response.headers["x-xss-protection"] == "0"


def test_security_header_referrer_policy(client: TestClient):
    """Referrer-Policy: strict-origin-when-cross-origin."""
    response = client.get("/ok")
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_security_header_permissions_policy(client: TestClient):
    """Permissions-Policy: camera=(), microphone=(), geolocation=()."""
    response = client.get("/ok")
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"


def test_hsts_production_only(client_production: TestClient):
    """HSTS header present when ENVIRONMENT=production."""
    response = client_production.get("/ok")
    hsts = response.headers.get("strict-transport-security")
    assert hsts is not None
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts


def test_hsts_absent_non_production(client: TestClient):
    """HSTS header absent when ENVIRONMENT=local."""
    response = client.get("/ok")
    assert "strict-transport-security" not in response.headers


# ---------------------------------------------------------------------------
# (a) CORS preflight OPTIONS coverage
# ---------------------------------------------------------------------------


def test_cors_preflight_gets_security_headers(client_cors: TestClient):
    """OPTIONS preflight response includes security headers.

    This proves middleware ordering: RequestPipelineMiddleware (outer)
    wraps CORSMiddleware (inner), so even when CORS handles the preflight
    and returns early, our middleware still applies security headers.
    """
    response = client_cors.options(
        "/ok",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-xss-protection"] == "0"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"


def test_cors_preflight_gets_request_id_header(client_cors: TestClient):
    """OPTIONS preflight response includes X-Request-ID."""
    response = client_cors.options(
        "/ok",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert _is_valid_uuid4(request_id)


# ---------------------------------------------------------------------------
# (b) AC13: X-Request-ID on error paths (4xx, 5xx, exceptions)
# ---------------------------------------------------------------------------


def test_request_id_header_on_4xx(client: TestClient):
    """404 response has X-Request-ID header."""
    response = client.get("/not-found")
    assert response.status_code == 404
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert _is_valid_uuid4(request_id)


def test_request_id_header_on_5xx(client: TestClient):
    """500 response has X-Request-ID header."""
    response = client.get("/server-error")
    assert response.status_code == 500
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert _is_valid_uuid4(request_id)


def test_request_id_header_on_unhandled_exception(client: TestClient):
    """Unhandled exception response has X-Request-ID header."""
    response = client.get("/unhandled")
    assert response.status_code == 500
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert _is_valid_uuid4(request_id)


# ---------------------------------------------------------------------------
# Log level by status code tests
# ---------------------------------------------------------------------------


def _capture_middleware_log(client: TestClient, path: str, **headers: str) -> list[dict]:
    """Make a request and capture JSON log lines from structlog."""
    buf = io.StringIO()
    original_config = structlog.get_config()
    try:
        setup_logging(_make_settings(LOG_FORMAT="json"))
        structlog.configure(
            **{**structlog.get_config(), "logger_factory": structlog.PrintLoggerFactory(file=buf)}
        )
        client.get(path, headers=headers)
    finally:
        structlog.configure(**original_config)

    lines = []
    for line in buf.getvalue().strip().splitlines():
        if line.strip():
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return lines


def test_log_level_info_for_2xx(client: TestClient):
    """200 response is logged at info level."""
    logs = _capture_middleware_log(client, "/ok")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    assert request_logs[0]["level"] == "info"


def test_log_level_warning_for_4xx(client: TestClient):
    """404 response is logged at warning level."""
    logs = _capture_middleware_log(client, "/not-found")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    assert request_logs[0]["level"] == "warning"


def test_log_level_error_for_5xx(client: TestClient):
    """500 response is logged at error level."""
    logs = _capture_middleware_log(client, "/server-error")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    assert request_logs[0]["level"] == "error"


# ---------------------------------------------------------------------------
# Request log field tests
# ---------------------------------------------------------------------------


def test_request_log_fields(client: TestClient):
    """Request log includes method, path, status_code, duration_ms."""
    logs = _capture_middleware_log(client, "/ok")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    entry = request_logs[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/ok"
    assert entry["status_code"] == 200
    assert "duration_ms" in entry
    assert isinstance(entry["duration_ms"], (int, float))
    assert entry["duration_ms"] >= 0


def test_user_id_logged_when_authenticated(client: TestClient):
    """user_id is included in log when request.state has user_id."""
    logs = _capture_middleware_log(client, "/authenticated")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    assert request_logs[0].get("user_id") == "user-42"


def test_user_id_absent_when_unauthenticated(client: TestClient):
    """user_id is not in log entry when no authentication."""
    logs = _capture_middleware_log(client, "/ok")
    request_logs = [entry for entry in logs if entry.get("event") == "request_completed"]
    assert len(request_logs) == 1
    assert "user_id" not in request_logs[0]


# ---------------------------------------------------------------------------
# (c) Negative tests: no secrets in logs
# ---------------------------------------------------------------------------


def test_authorization_header_not_logged(client: TestClient):
    """Request with Authorization: Bearer <token> must NOT appear in log output."""
    secret_token = "super-secret-jwt-token-value-12345"
    logs = _capture_middleware_log(
        client, "/ok", Authorization=f"Bearer {secret_token}"
    )
    # Flatten all log content to a single string for inspection
    raw = json.dumps(logs)
    assert secret_token not in raw
    assert "Bearer" not in raw
    # Also check for the header key itself
    assert "authorization" not in raw.lower()


def test_cookie_header_not_logged(client: TestClient):
    """Request with Cookie header must NOT appear in log output."""
    secret_cookie = "session=abc123secret456"
    logs = _capture_middleware_log(
        client, "/ok", Cookie=secret_cookie
    )
    raw = json.dumps(logs)
    assert secret_cookie not in raw
    assert "abc123secret456" not in raw
