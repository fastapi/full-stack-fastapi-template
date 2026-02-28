"""Shared async HTTP client wrapper.

Provides a reusable httpx.AsyncClient with:
  - Configurable connect / read timeouts (5s / 30s defaults)
  - Automatic retry with exponential backoff on 502, 503, 504
  - Simple circuit breaker: opens after N failures within a time window
  - X-Request-ID / X-Correlation-ID header propagation from structlog contextvars

Usage::

    # In a FastAPI lifespan or startup event:
    app.state.http_client = HttpClient()

    # In a route handler:
    from app.core.http_client import get_http_client

    @router.get("/external")
    async def call_external(http: HttpClient = Depends(get_http_client)):
        response = await http.get("https://api.example.com/data")
        return response.json()
"""

import asyncio
import time
from typing import Any

import httpx
import structlog
from fastapi import Request

from app.core.errors import ServiceError

# Retry-able HTTP status codes (gateway errors)
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({502, 503, 504})

# Backoff delays in seconds for attempt 0, 1, 2 (applies before retries 1, 2, 3)
_BACKOFF_TIMES: list[float] = [0.5, 1.0, 2.0]


class CircuitBreaker:
    """Simple circuit breaker.

    Tracks recent failure timestamps within a sliding window. When the number
    of failures within the window reaches the threshold, the circuit opens and
    stays open until the window duration passes (at which point it enters a
    half-open state that allows the next request through).
    """

    def __init__(self, threshold: int = 5, window: float = 60.0) -> None:
        self._threshold = threshold
        self._window = window
        self._failures: list[float] = []  # monotonic timestamps of recent failures
        self._open_until: float | None = None  # time after which circuit may close

    @property
    def is_open(self) -> bool:
        """Return True when the circuit is open (requests should be blocked)."""
        if self._open_until is None:
            return False
        if time.monotonic() >= self._open_until:
            # Half-open: allow one request through and reset state
            self._open_until = None
            self._failures.clear()
            return False
        return True

    def record_failure(self) -> None:
        """Record a failure. Opens the circuit if threshold is reached."""
        now = time.monotonic()
        # Prune failures that have fallen outside the sliding window
        self._failures = [t for t in self._failures if now - t < self._window]
        self._failures.append(now)
        if len(self._failures) >= self._threshold:
            self._open_until = now + self._window

    def record_success(self) -> None:
        """Record a success. Resets all failure state and closes the circuit."""
        self._failures.clear()
        self._open_until = None


class HttpClient:
    """Shared async HTTP client with retry, circuit breaker, and header propagation.

    Intended to be created once and stored on ``app.state.http_client`` so it
    is reused across requests (connection pooling).
    """

    def __init__(
        self,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        timeout = httpx.Timeout(
            read_timeout, connect=connect_timeout, read=read_timeout
        )
        self._client = httpx.AsyncClient(timeout=timeout)
        self._max_retries = max_retries
        self._circuit_breaker = CircuitBreaker()
        self._logger = structlog.get_logger()

    def _get_propagation_headers(self) -> dict[str, str]:
        """Read request_id and correlation_id from structlog contextvars.

        Returns a dict of headers to add to the outgoing request.
        """
        ctx = structlog.contextvars.get_contextvars()
        headers: dict[str, str] = {}
        if "request_id" in ctx:
            headers["X-Request-ID"] = ctx["request_id"]
        if "correlation_id" in ctx:
            headers["X-Correlation-ID"] = ctx["correlation_id"]
        return headers

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make an HTTP request with retry, circuit breaker, and header propagation.

        Retries are attempted on 502, 503, 504 responses with exponential
        backoff (0.5s, 1.0s, 2.0s). 4xx responses are not retried. After all
        retries are exhausted the last non-retried response is returned. If a
        network-level exception persists after retries it is re-raised.

        Raises:
            ServiceError: 503 when the circuit breaker is open.
            httpx.HTTPError: When network errors persist after all retries.
        """
        if self._circuit_breaker.is_open:
            raise ServiceError(
                status_code=503,
                message="Circuit breaker is open",
                code="SERVICE_UNAVAILABLE",
            )

        # Merge propagation headers into any caller-supplied headers
        headers: dict[str, str] = dict(kwargs.pop("headers", {}) or {})
        headers.update(self._get_propagation_headers())
        kwargs["headers"] = headers

        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)

                if (
                    response.status_code in _RETRYABLE_STATUS_CODES
                    and attempt < self._max_retries
                ):
                    self._logger.warning(
                        "http_client_retry",
                        method=method,
                        url=url,
                        status_code=response.status_code,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(
                        _BACKOFF_TIMES[min(attempt, len(_BACKOFF_TIMES) - 1)]
                    )
                    continue

                # Record outcome with circuit breaker
                if response.status_code >= 500:
                    self._circuit_breaker.record_failure()
                else:
                    self._circuit_breaker.record_success()

                return response

            except httpx.HTTPError as exc:
                last_exc = exc
                self._circuit_breaker.record_failure()
                if attempt < self._max_retries:
                    self._logger.warning(
                        "http_client_retry",
                        method=method,
                        url=url,
                        error=str(exc),
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(
                        _BACKOFF_TIMES[min(attempt, len(_BACKOFF_TIMES) - 1)]
                    )
                else:
                    self._logger.error(
                        "http_client_exhausted_retries",
                        method=method,
                        url=url,
                        error=str(exc),
                    )
                    raise

        # Safety net: should not be reached given the loop structure above.
        # last_exc is only set when we exhausted retries via exception path (already raised).
        raise last_exc or ServiceError(
            status_code=503,
            message="HTTP request failed after all retries",
            code="SERVICE_UNAVAILABLE",
        )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a PATCH request."""
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def close(self) -> None:
        """Close the underlying httpx client and release connections."""
        await self._client.aclose()


def get_http_client(request: Request) -> HttpClient:
    """FastAPI dependency: return the shared HttpClient from app state.

    The client must be initialised during application startup and stored at
    ``app.state.http_client``.

    Raises:
        ServiceError: 503 when the client has not been initialised.
    """
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise ServiceError(
            status_code=503,
            message="HTTP client not initialized",
            code="SERVICE_UNAVAILABLE",
        )
    return client  # type: ignore[no-any-return]
