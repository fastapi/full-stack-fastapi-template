"""Integration tests for unified error response shape across the full app.

Verifies that ALL error status codes (401, 404, 422, 500) return the unified
JSON error shape when using the full assembled app. Tests the complete
middleware + error handler pipeline end-to-end.

Uses conftest.py fixtures:
  - client                 — authenticated TestClient (Supabase + auth overridden)
  - unauthenticated_client — TestClient with only Supabase overridden (401 on auth endpoints)
  - mock_supabase          — MagicMock Supabase client (shared with client fixture)

Run:
  uv run pytest backend/tests/integration/test_error_responses.py -v
"""

import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

_PREFIX = "/api/v1"

# ---------------------------------------------------------------------------
# Security headers expected on every response
# ---------------------------------------------------------------------------

_EXPECTED_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


# ---------------------------------------------------------------------------
# TestUnifiedErrorShape — verifies shape for 401 / 404 / 422 / 500
# ---------------------------------------------------------------------------


class TestUnifiedErrorShape:
    """Each error status code returns the unified JSON error shape."""

    def test_401_returns_unified_error_shape(
        self, unauthenticated_client: TestClient
    ) -> None:
        """Unauthenticated request returns 401 with unified error body."""
        response = unauthenticated_client.get(f"{_PREFIX}/entities/")

        assert response.status_code == 401
        body = response.json()
        assert "error" in body
        assert "message" in body
        assert "code" in body
        assert "request_id" in body
        assert body["error"] == "UNAUTHORIZED"

    def test_404_returns_unified_error_shape(
        self, client: TestClient, mock_supabase: MagicMock
    ) -> None:
        """Request for a non-existent entity returns 404 with ENTITY_NOT_FOUND."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = APIError(
            {"message": "No rows found", "code": "PGRST116"}
        )

        nonexistent_id = str(uuid.uuid4())
        response = client.get(f"{_PREFIX}/entities/{nonexistent_id}")

        assert response.status_code == 404
        body = response.json()
        assert "error" in body
        assert "message" in body
        assert "code" in body
        assert "request_id" in body
        assert body["error"] == "NOT_FOUND"
        assert body["code"] == "ENTITY_NOT_FOUND"

    def test_422_returns_unified_error_shape(self, client: TestClient) -> None:
        """POST with missing required field returns 422 with details array."""
        response = client.post(
            f"{_PREFIX}/entities/",
            json={"description": "no title"},
        )

        assert response.status_code == 422
        body = response.json()
        assert "error" in body
        assert "message" in body
        assert "code" in body
        assert "request_id" in body
        assert "details" in body
        assert body["error"] == "VALIDATION_ERROR"
        assert isinstance(body["details"], list)
        assert len(body["details"]) >= 1
        for detail in body["details"]:
            assert "field" in detail
            assert "message" in detail
            assert "type" in detail

    def test_500_returns_unified_error_shape(
        self, client: TestClient, mock_supabase: MagicMock
    ) -> None:
        """Unhandled server exception returns 500 without leaking internal details."""
        mock_supabase.table.side_effect = RuntimeError("db crash")

        response = client.get(f"{_PREFIX}/entities/")

        assert response.status_code == 500
        body = response.json()
        assert "error" in body
        assert "message" in body
        assert "code" in body
        assert "request_id" in body
        assert body["error"] == "INTERNAL_ERROR"
        assert "db crash" not in body["message"]


# ---------------------------------------------------------------------------
# TestErrorResponseMetadata — request_id and security headers
# ---------------------------------------------------------------------------


class TestErrorResponseMetadata:
    """Error responses include valid request_id and security headers."""

    def test_error_response_includes_valid_request_id(
        self, unauthenticated_client: TestClient
    ) -> None:
        """request_id in error body is a valid UUID string."""
        response = unauthenticated_client.get(f"{_PREFIX}/entities/")

        body = response.json()
        assert "request_id" in body
        # Raises ValueError if not a valid UUID — that is the assertion.
        uuid.UUID(body["request_id"])

    def test_error_response_has_security_headers(
        self, unauthenticated_client: TestClient
    ) -> None:
        """All five security headers are present on error responses."""
        response = unauthenticated_client.get(f"{_PREFIX}/entities/")

        for header, expected_value in _EXPECTED_SECURITY_HEADERS.items():
            assert header in response.headers, f"Missing security header: {header}"
            assert response.headers[header] == expected_value, (
                f"Header {header!r}: expected {expected_value!r}, "
                f"got {response.headers[header]!r}"
            )

    def test_error_response_has_request_id_header(
        self, unauthenticated_client: TestClient
    ) -> None:
        """X-Request-ID response header is present and is a valid UUID."""
        response = unauthenticated_client.get(f"{_PREFIX}/entities/")

        assert "X-Request-ID" in response.headers, "Missing X-Request-ID header"
        # Raises ValueError if not a valid UUID — that is the assertion.
        uuid.UUID(response.headers["X-Request-ID"])
