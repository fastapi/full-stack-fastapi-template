"""Unit tests for the shared HTTP client wrapper.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/http_client.py

Does NOT make real HTTP calls — uses httpx.MockTransport for isolation.
Run with:
  uv run pytest tests/unit/test_http_client.py -v
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import structlog
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.errors import ServiceError, register_exception_handlers
from app.core.http_client import CircuitBreaker, HttpClient, get_http_client

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_client(handler) -> httpx.AsyncClient:  # type: ignore[type-arg]
    """Wrap a handler function into an AsyncClient using MockTransport."""
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


# ---------------------------------------------------------------------------
# CircuitBreaker unit tests (pure logic, no HTTP)
# ---------------------------------------------------------------------------


def test_circuit_breaker_initially_closed():
    """Circuit breaker starts in the closed (allow) state."""
    cb = CircuitBreaker(threshold=5, window=60.0)
    assert cb.is_open is False


def test_circuit_breaker_opens_after_threshold():
    """Circuit opens after `threshold` failures within the window."""
    cb = CircuitBreaker(threshold=5, window=60.0)
    for _ in range(5):
        cb.record_failure()
    assert cb.is_open is True


def test_circuit_breaker_does_not_open_below_threshold():
    """Circuit stays closed when failures are below threshold."""
    cb = CircuitBreaker(threshold=5, window=60.0)
    for _ in range(4):
        cb.record_failure()
    assert cb.is_open is False


def test_circuit_breaker_success_resets_state():
    """record_success clears failures and closes circuit."""
    cb = CircuitBreaker(threshold=5, window=60.0)
    for _ in range(5):
        cb.record_failure()
    assert cb.is_open is True
    cb.record_success()
    assert cb.is_open is False


def test_circuit_breaker_half_open_after_window():
    """Circuit transitions to half-open (allows one request) after window expires."""
    cb = CircuitBreaker(threshold=5, window=60.0)
    for _ in range(5):
        cb.record_failure()
    assert cb.is_open is True

    # Simulate time passing beyond the window using monotonic mock
    future_time = time.monotonic() + 61.0
    with patch("app.core.http_client.time.monotonic", return_value=future_time):
        # Half-open: circuit should report closed (allow one through)
        assert cb.is_open is False


def test_circuit_breaker_old_failures_expire():
    """Failures older than the window are pruned and do not count."""
    cb = CircuitBreaker(threshold=5, window=60.0)

    # Record 4 failures "in the past" (70 seconds ago)
    past_time = time.monotonic() - 70.0
    cb._failures = [past_time, past_time, past_time, past_time]

    # Record one fresh failure — should not trigger open because old ones expired
    cb.record_failure()
    assert cb.is_open is False


# ---------------------------------------------------------------------------
# HttpClient — timeout configuration
# ---------------------------------------------------------------------------


def test_timeout_configuration():
    """HttpClient uses 5s connect timeout and 30s read timeout by default."""
    client = HttpClient()
    timeout = client._client.timeout
    assert timeout.connect == 5.0
    assert timeout.read == 30.0


def test_timeout_configuration_custom():
    """HttpClient accepts custom timeout values."""
    client = HttpClient(connect_timeout=2.0, read_timeout=10.0)
    timeout = client._client.timeout
    assert timeout.connect == 2.0
    assert timeout.read == 10.0


# ---------------------------------------------------------------------------
# HttpClient — header propagation
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_header_propagation_request_id():
    """X-Request-ID and X-Correlation-ID are forwarded from structlog contextvars."""
    captured_headers: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id="req-abc-123",
        correlation_id="corr-xyz-456",
    )
    try:
        with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
            await client.get("http://example.com/test")
    finally:
        structlog.contextvars.clear_contextvars()
        await client.close()

    assert captured_headers.get("x-request-id") == "req-abc-123"
    assert captured_headers.get("x-correlation-id") == "corr-xyz-456"


@pytest.mark.anyio
async def test_header_propagation_no_contextvars():
    """No propagation headers added when contextvars are empty."""
    captured_headers: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    structlog.contextvars.clear_contextvars()
    try:
        with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
            await client.get("http://example.com/test")
    finally:
        await client.close()

    assert "x-request-id" not in captured_headers
    assert "x-correlation-id" not in captured_headers


@pytest.mark.anyio
async def test_header_propagation_merges_with_existing_headers():
    """Propagation headers are merged with any headers already in the request."""
    captured_headers: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id="req-111")
    try:
        with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
            await client.get(
                "http://example.com/test",
                headers={"Authorization": "Bearer token"},
            )
    finally:
        structlog.contextvars.clear_contextvars()
        await client.close()

    assert captured_headers.get("x-request-id") == "req-111"
    assert captured_headers.get("authorization") == "Bearer token"


# ---------------------------------------------------------------------------
# HttpClient — retry on 5xx gateway errors
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_retry_on_502():
    """Returns 200 after one 502 retry."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(502 if call_count == 1 else 200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 200
    assert call_count == 2
    mock_sleep.assert_awaited_once_with(0.5)


@pytest.mark.anyio
async def test_retry_on_503():
    """Returns 200 after one 503 retry."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(503 if call_count == 1 else 200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 200
    assert call_count == 2
    mock_sleep.assert_awaited_once_with(0.5)


@pytest.mark.anyio
async def test_retry_on_504():
    """Returns 200 after one 504 retry."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(504 if call_count == 1 else 200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 200
    assert call_count == 2
    mock_sleep.assert_awaited_once_with(0.5)


@pytest.mark.anyio
async def test_exponential_backoff_sequence():
    """Backoff delays follow 0.5s -> 1.0s -> 2.0s sequence across 3 retries."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        # Always 502 for first 3 calls, success on 4th
        return httpx.Response(502 if call_count < 4 else 200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 200
    assert call_count == 4
    calls = [c.args[0] for c in mock_sleep.await_args_list]
    assert calls == [0.5, 1.0, 2.0]


# ---------------------------------------------------------------------------
# HttpClient — no retry on 4xx
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_no_retry_on_4xx():
    """400 response is not retried — transport called only once."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(400)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 400
    assert call_count == 1
    mock_sleep.assert_not_awaited()


@pytest.mark.anyio
async def test_no_retry_on_401():
    """401 response is not retried."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 401
    assert call_count == 1
    mock_sleep.assert_not_awaited()


@pytest.mark.anyio
async def test_no_retry_on_404():
    """404 response is not retried."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(404)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch(
        "app.core.http_client.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 404
    assert call_count == 1
    mock_sleep.assert_not_awaited()


# ---------------------------------------------------------------------------
# HttpClient — retries exhausted returns last response
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_retries_exhausted_returns_last_502():
    """After 4 total calls (1 + 3 retries) all returning 502, final 502 is returned."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(502)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        response = await client.get("http://example.com/")
        await client.close()

    assert response.status_code == 502
    assert call_count == 4  # 1 initial + 3 retries


@pytest.mark.anyio
async def test_retries_exhausted_on_http_error_raises():
    """After retries exhausted on httpx.HTTPError, the exception propagates."""
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        raise httpx.ConnectError("Connection refused", request=request)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(httpx.ConnectError):
            await client.get("http://example.com/")
        await client.close()

    assert call_count == 4  # 1 initial + 3 retries


# ---------------------------------------------------------------------------
# HttpClient — circuit breaker integration
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_circuit_open_raises_service_error_without_http_call():
    """When circuit is open, request raises 503 ServiceError without calling transport."""
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    # Force circuit open by recording 5 failures directly
    for _ in range(5):
        client._circuit_breaker.record_failure()
    assert client._circuit_breaker.is_open is True

    with pytest.raises(ServiceError) as exc_info:
        await client.get("http://example.com/")
    await client.close()

    assert exc_info.value.status_code == 503
    assert call_count == 0  # Transport never called


@pytest.mark.anyio
async def test_circuit_breaker_records_failure_on_5xx():
    """5xx response records a failure in the circuit breaker."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    # Use 0 retries for speed
    client._max_retries = 0

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        await client.get("http://example.com/")
    await client.close()

    assert len(client._circuit_breaker._failures) == 1


@pytest.mark.anyio
async def test_circuit_breaker_records_success_on_2xx():
    """2xx response records a success (clears failure state) in circuit breaker."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    # Pre-seed some failures
    client._circuit_breaker.record_failure()
    client._circuit_breaker.record_failure()

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        await client.get("http://example.com/")
    await client.close()

    assert len(client._circuit_breaker._failures) == 0
    assert client._circuit_breaker._open_until is None


# ---------------------------------------------------------------------------
# HttpClient — convenience methods
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_method():
    """get() sends a GET request."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        response = await client.get("http://example.com/")
    await client.close()

    assert captured["method"] == "GET"
    assert response.status_code == 200


@pytest.mark.anyio
async def test_post_method():
    """post() sends a POST request."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        return httpx.Response(201)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        response = await client.post("http://example.com/", json={"key": "value"})
    await client.close()

    assert captured["method"] == "POST"
    assert response.status_code == 201


@pytest.mark.anyio
async def test_put_method():
    """put() sends a PUT request."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        await client.put("http://example.com/1")
    await client.close()

    assert captured["method"] == "PUT"


@pytest.mark.anyio
async def test_patch_method():
    """patch() sends a PATCH request."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        return httpx.Response(200)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        await client.patch("http://example.com/1")
    await client.close()

    assert captured["method"] == "PATCH"


@pytest.mark.anyio
async def test_delete_method():
    """delete() sends a DELETE request."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        return httpx.Response(204)

    client = HttpClient()
    client._client = _make_mock_client(handler)

    with patch("app.core.http_client.asyncio.sleep", new_callable=AsyncMock):
        response = await client.delete("http://example.com/1")
    await client.close()

    assert captured["method"] == "DELETE"
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# get_http_client FastAPI dependency
# ---------------------------------------------------------------------------


def test_get_http_client_returns_from_app_state():
    """Dependency returns the HttpClient stored in app.state."""
    app = FastAPI()
    register_exception_handlers(app)
    mock_client = MagicMock(spec=HttpClient)
    app.state.http_client = mock_client

    @app.get("/test")
    def endpoint(http_client=Depends(get_http_client)):  # noqa: ARG001, B008
        return {"ok": True}

    with TestClient(app) as tc:
        resp = tc.get("/test")

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_get_http_client_missing_raises_503():
    """Dependency raises 503 ServiceError when app.state has no http_client."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test")
    def endpoint(http_client=Depends(get_http_client)):  # noqa: ARG001, B008
        return {"ok": True}

    with TestClient(app, raise_server_exceptions=False) as tc:
        resp = tc.get("/test")

    assert resp.status_code == 503
    body = resp.json()
    assert body["code"] == "SERVICE_UNAVAILABLE"
