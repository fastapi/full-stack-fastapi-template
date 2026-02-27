"""Unit tests for the unified error handling framework.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/errors.py

Uses a minimal FastAPI app with handlers registered — does NOT import
the real app from main.py, so no DB or config fixtures are required.
Run with:
  uv run pytest backend/tests/unit/test_errors.py -v --noconftest
"""

import uuid

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import (
    STATUS_CODE_MAP,
    ServiceError,
    register_exception_handlers,
)

# ---------------------------------------------------------------------------
# Model used to trigger validation errors
# ---------------------------------------------------------------------------


class ItemModel(BaseModel):
    title: str
    count: int


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_app() -> FastAPI:
    """Create a minimal FastAPI app with error handlers registered."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-http/{status_code}")
    async def raise_http_exception(status_code: int):
        raise HTTPException(status_code=status_code, detail="Test error")

    @app.get("/raise-service-error")
    async def raise_service_error():
        raise ServiceError(
            status_code=404,
            message="Entity not found",
            code="ENTITY_NOT_FOUND",
        )

    @app.get("/raise-unhandled")
    async def raise_unhandled():
        raise RuntimeError("Something broke")

    @app.post("/validate")
    async def validate_body(item: ItemModel):
        return item

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# ServiceError unit tests (no HTTP — just the class itself)
# ---------------------------------------------------------------------------


def test_service_error_attributes():
    """ServiceError has status_code, message, code, and error attributes."""
    err = ServiceError(
        status_code=404,
        message="Entity not found",
        code="ENTITY_NOT_FOUND",
    )
    assert err.status_code == 404
    assert err.message == "Entity not found"
    assert err.code == "ENTITY_NOT_FOUND"
    assert err.error == "NOT_FOUND"


def test_service_error_unknown_status_defaults_internal():
    """An unrecognised HTTP status code maps error to INTERNAL_ERROR."""
    err = ServiceError(
        status_code=418,
        message="I'm a teapot",
        code="TEAPOT",
    )
    assert err.status_code == 418
    assert err.error == "INTERNAL_ERROR"


def test_service_error_is_exception():
    """ServiceError is raise-able as a standard Python exception."""
    with pytest.raises(ServiceError) as exc_info:
        raise ServiceError(
            status_code=403,
            message="Access denied",
            code="FORBIDDEN",
        )
    assert exc_info.value.status_code == 403
    assert str(exc_info.value) == "Access denied"


# ---------------------------------------------------------------------------
# STATUS_CODE_MAP tests
# ---------------------------------------------------------------------------


def test_status_code_map_coverage():
    """STATUS_CODE_MAP contains all expected HTTP status entries."""
    expected = {400, 401, 403, 404, 409, 422, 429, 500, 503}
    assert expected.issubset(set(STATUS_CODE_MAP.keys()))


def test_status_code_map_values():
    """STATUS_CODE_MAP maps known codes to correct category strings."""
    assert STATUS_CODE_MAP[400] == "BAD_REQUEST"
    assert STATUS_CODE_MAP[401] == "UNAUTHORIZED"
    assert STATUS_CODE_MAP[403] == "FORBIDDEN"
    assert STATUS_CODE_MAP[404] == "NOT_FOUND"
    assert STATUS_CODE_MAP[409] == "CONFLICT"
    assert STATUS_CODE_MAP[422] == "VALIDATION_ERROR"
    assert STATUS_CODE_MAP[429] == "RATE_LIMITED"
    assert STATUS_CODE_MAP[500] == "INTERNAL_ERROR"
    assert STATUS_CODE_MAP[503] == "SERVICE_UNAVAILABLE"


# ---------------------------------------------------------------------------
# HTTPException handler tests
# ---------------------------------------------------------------------------


def test_http_exception_404_handler(client: TestClient):
    """404 HTTPException returns NOT_FOUND error shape."""
    response = client.get("/raise-http/404")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "NOT_FOUND"
    assert body["message"] == "Test error"
    assert body["code"] == "NOT_FOUND"
    assert "request_id" in body


def test_http_exception_401_handler(client: TestClient):
    """401 HTTPException returns UNAUTHORIZED error shape."""
    response = client.get("/raise-http/401")
    assert response.status_code == 401
    body = response.json()
    assert body["error"] == "UNAUTHORIZED"
    assert body["code"] == "UNAUTHORIZED"
    assert "request_id" in body


def test_http_exception_403_handler(client: TestClient):
    """403 HTTPException returns FORBIDDEN error shape."""
    response = client.get("/raise-http/403")
    assert response.status_code == 403
    body = response.json()
    assert body["error"] == "FORBIDDEN"
    assert body["code"] == "FORBIDDEN"
    assert "request_id" in body


def test_http_exception_with_no_detail(client: TestClient):
    """HTTPException without explicit detail uses default status text."""
    from fastapi import FastAPI

    app = client.app
    assert isinstance(app, FastAPI)

    @app.get("/raise-http-no-detail")
    async def raise_no_detail():
        raise HTTPException(status_code=404)

    response = client.get("/raise-http-no-detail")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "NOT_FOUND"
    # HTTPException defaults detail to the HTTP status phrase
    assert body["message"] == "Not Found"
    assert body["code"] == "NOT_FOUND"
    assert "request_id" in body


def test_http_exception_500_handler(client: TestClient):
    """500 HTTPException returns INTERNAL_ERROR error shape."""
    response = client.get("/raise-http/500")
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_ERROR"
    assert body["code"] == "INTERNAL_ERROR"
    assert "request_id" in body


# ---------------------------------------------------------------------------
# ServiceError handler tests
# ---------------------------------------------------------------------------


def test_service_error_handler(client: TestClient):
    """ServiceError returns correct HTTP status and ENTITY_NOT_FOUND code."""
    response = client.get("/raise-service-error")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "NOT_FOUND"
    assert body["message"] == "Entity not found"
    assert body["code"] == "ENTITY_NOT_FOUND"
    assert "request_id" in body


# ---------------------------------------------------------------------------
# Validation error handler tests
# ---------------------------------------------------------------------------


def test_validation_error_handler(client: TestClient):
    """Invalid request body returns 422 VALIDATION_ERROR with details array."""
    # Missing required 'title', and 'count' is the wrong type
    response = client.post("/validate", json={"count": "not-a-number"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert body["code"] == "VALIDATION_FAILED"
    assert body["message"] == "Request validation failed."
    assert "details" in body
    assert isinstance(body["details"], list)
    assert len(body["details"]) >= 1
    # Each detail has field, message, type
    for detail in body["details"]:
        assert "field" in detail
        assert "message" in detail
        assert "type" in detail


def test_validation_error_details_field_path(client: TestClient):
    """Validation error details use 'title', not 'body.title' as field path."""
    # Missing 'title' field entirely — only send count with valid value
    response = client.post("/validate", json={"count": 5})
    assert response.status_code == 422
    body = response.json()
    details = body["details"]
    field_names = [d["field"] for d in details]
    # title is missing — its field name should be 'title', not 'body.title'
    assert "title" in field_names
    for name in field_names:
        assert not name.startswith("body.")
        assert not name.startswith("query.")
        assert not name.startswith("path.")


# ---------------------------------------------------------------------------
# Unhandled exception handler tests
# ---------------------------------------------------------------------------


def test_unhandled_exception_handler(client: TestClient):
    """Unhandled RuntimeError returns 500 INTERNAL_ERROR without leaking details."""
    response = client.get("/raise-unhandled")
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "INTERNAL_ERROR"
    assert body["code"] == "INTERNAL_ERROR"
    assert body["message"] == "An unexpected error occurred."
    assert "request_id" in body


# ---------------------------------------------------------------------------
# request_id tests
# ---------------------------------------------------------------------------


def _is_valid_uuid(value: str) -> bool:
    """Return True if value is a valid UUID string."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def test_error_response_has_request_id(client: TestClient):
    """All error handler responses include a non-empty UUID request_id."""
    endpoints = [
        ("GET", "/raise-http/404"),
        ("GET", "/raise-http/401"),
        ("GET", "/raise-service-error"),
        ("GET", "/raise-unhandled"),
    ]
    for method, path in endpoints:
        response = client.request(method, path)
        body = response.json()
        assert "request_id" in body, f"Missing request_id for {path}"
        assert body["request_id"], f"Empty request_id for {path}"
        assert _is_valid_uuid(body["request_id"]), (
            f"request_id is not a valid UUID for {path}: {body['request_id']!r}"
        )


def test_validation_error_response_has_request_id(client: TestClient):
    """Validation error response also includes a valid UUID request_id."""
    response = client.post("/validate", json={"count": "bad"})
    body = response.json()
    assert "request_id" in body
    assert _is_valid_uuid(body["request_id"])
