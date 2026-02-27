"""Unit tests for shared Pydantic models.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/models/common.py
  - backend/app/models/auth.py
"""

from pydantic import BaseModel

from app.models.auth import Principal
from app.models.common import (
    ErrorResponse,
    PaginatedResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)

# ---------------------------------------------------------------------------
# ErrorResponse tests
# ---------------------------------------------------------------------------


def test_error_response_serialization():
    """ErrorResponse serializes all four required fields."""
    resp = ErrorResponse(
        error="NOT_FOUND",
        message="Entity not found",
        code="ENTITY_NOT_FOUND",
        request_id="abc-123",
    )
    data = resp.model_dump()
    assert data["error"] == "NOT_FOUND"
    assert data["message"] == "Entity not found"
    assert data["code"] == "ENTITY_NOT_FOUND"
    assert data["request_id"] == "abc-123"


def test_error_response_json_schema():
    """ErrorResponse.model_json_schema() includes all expected field names."""
    schema = ErrorResponse.model_json_schema()
    properties = schema.get("properties", {})
    assert "error" in properties
    assert "message" in properties
    assert "code" in properties
    assert "request_id" in properties


# ---------------------------------------------------------------------------
# ValidationErrorResponse tests
# ---------------------------------------------------------------------------


def test_validation_error_response_has_details():
    """ValidationErrorResponse serializes details list with field/message/type."""
    resp = ValidationErrorResponse(
        error="BAD_REQUEST",
        message="Validation failed",
        code="VALIDATION_ERROR",
        request_id="req-456",
        details=[
            ValidationErrorDetail(
                field="email",
                message="Value is not a valid email address",
                type="value_error",
            ),
            ValidationErrorDetail(
                field="name",
                message="Field is required",
                type="missing",
            ),
        ],
    )
    data = resp.model_dump()
    assert len(data["details"]) == 2
    first = data["details"][0]
    assert first["field"] == "email"
    assert first["message"] == "Value is not a valid email address"
    assert first["type"] == "value_error"
    second = data["details"][1]
    assert second["field"] == "name"
    assert second["type"] == "missing"


def test_validation_error_response_inherits_error_fields():
    """ValidationErrorResponse inherits all fields from ErrorResponse parent."""
    resp = ValidationErrorResponse(
        error="UNPROCESSABLE_ENTITY",
        message="Input validation failed",
        code="INVALID_INPUT",
        request_id="req-789",
        details=[],
    )
    data = resp.model_dump()
    assert data["error"] == "UNPROCESSABLE_ENTITY"
    assert data["message"] == "Input validation failed"
    assert data["code"] == "INVALID_INPUT"
    assert data["request_id"] == "req-789"
    assert data["details"] == []


# ---------------------------------------------------------------------------
# PaginatedResponse tests
# ---------------------------------------------------------------------------


def test_paginated_response_generic():
    """PaginatedResponse[dict] serializes data list and count correctly."""
    items = [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]
    resp = PaginatedResponse[dict](data=items, count=2)
    data = resp.model_dump()
    assert data["count"] == 2
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "alpha"
    assert data["data"][1]["name"] == "beta"


def test_paginated_response_with_typed_items():
    """PaginatedResponse works correctly with a typed Pydantic model."""

    class SimpleItem(BaseModel):
        id: int
        label: str

    items = [SimpleItem(id=10, label="foo"), SimpleItem(id=20, label="bar")]
    resp: PaginatedResponse[SimpleItem] = PaginatedResponse[SimpleItem](
        data=items, count=len(items)
    )
    data = resp.model_dump()
    assert data["count"] == 2
    assert data["data"][0] == {"id": 10, "label": "foo"}
    assert data["data"][1] == {"id": 20, "label": "bar"}


# ---------------------------------------------------------------------------
# Principal tests
# ---------------------------------------------------------------------------


def test_principal_defaults():
    """Principal defaults roles to [] and org_id to None when not supplied."""
    principal = Principal(user_id="user_abc123")
    assert principal.user_id == "user_abc123"
    assert principal.roles == []
    assert principal.org_id is None


def test_principal_full():
    """Principal serializes correctly when all fields are provided."""
    principal = Principal(
        user_id="user_xyz",
        roles=["admin", "editor"],
        org_id="org_001",
    )
    data = principal.model_dump()
    assert data["user_id"] == "user_xyz"
    assert data["roles"] == ["admin", "editor"]
    assert data["org_id"] == "org_001"
