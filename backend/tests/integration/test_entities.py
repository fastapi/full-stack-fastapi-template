"""Integration tests for Entity CRUD endpoints (/api/v1/entities).

Uses a minimal FastAPI app with dependency overrides for Supabase and auth.
All external dependencies are mocked — no running database required.

Run:
  uv run pytest backend/tests/integration/test_entities.py -v
"""

import os
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("CLERK_SECRET_KEY", "test-clerk-key")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

from app.api.routes.entities import router as entities_router
from app.core.auth import get_current_principal
from app.core.errors import register_exception_handlers
from app.core.supabase import get_supabase
from app.models.auth import Principal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX = "/api/v1"
_TEST_USER_ID = "user_test123"
_OTHER_USER_ID = "user_other456"
_ENTITY_ID = str(uuid.uuid4())
_NOW = datetime.now(tz=timezone.utc).isoformat()

_ENTITY_ROW = {
    "id": _ENTITY_ID,
    "title": "Test Entity",
    "description": "A test entity",
    "owner_id": _TEST_USER_ID,
    "created_at": _NOW,
    "updated_at": _NOW,
}

_TEST_PRINCIPAL = Principal(
    user_id=_TEST_USER_ID,
    session_id="sess_test",
    roles=[],
    org_id=None,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(
    supabase_mock: MagicMock | None = None,
    *,
    with_auth: bool = True,
) -> FastAPI:
    """Create a minimal FastAPI app with the entities router.

    Args:
        supabase_mock: Mock Supabase client. If None, a default MagicMock is used.
        with_auth: If True, overrides PrincipalDep with test principal.
                   If False, leaves real auth in place (will fail without JWT).
    """
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(entities_router, prefix=_PREFIX)

    mock_supabase = supabase_mock or MagicMock()

    app.dependency_overrides[get_supabase] = lambda: mock_supabase

    if with_auth:
        app.dependency_overrides[get_current_principal] = lambda: _TEST_PRINCIPAL

    return app


def _supabase_insert_mock(return_data: list[dict] | None = None) -> MagicMock:
    """Return a mock Supabase client configured for INSERT."""
    mock = MagicMock()
    response = MagicMock()
    response.data = return_data if return_data is not None else [_ENTITY_ROW]
    mock.table.return_value.insert.return_value.execute.return_value = response
    return mock


def _supabase_select_single_mock(
    return_data: dict | None = None,
    *,
    raise_api_error: bool = False,
) -> MagicMock:
    """Return a mock Supabase client configured for SELECT...single()."""
    mock = MagicMock()
    if raise_api_error:
        mock.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = APIError(
            {"message": "No rows found", "code": "PGRST116"}
        )
    else:
        response = MagicMock()
        response.data = return_data if return_data is not None else _ENTITY_ROW
        mock.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = response
    return mock


def _supabase_select_list_mock(
    return_data: list[dict] | None = None,
    count: int = 1,
) -> MagicMock:
    """Return a mock Supabase client configured for SELECT with pagination."""
    mock = MagicMock()
    response = MagicMock()
    response.data = return_data if return_data is not None else [_ENTITY_ROW]
    response.count = count
    mock.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value = response
    return mock


def _supabase_update_mock(return_data: list[dict] | None = None) -> MagicMock:
    """Return a mock Supabase client configured for UPDATE."""
    mock = MagicMock()
    response = MagicMock()
    response.data = return_data if return_data is not None else [_ENTITY_ROW]
    mock.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = response
    # Also mock select for get_entity (no-op update path).
    select_response = MagicMock()
    select_response.data = _ENTITY_ROW
    mock.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = select_response
    return mock


def _supabase_delete_mock(
    return_data: list[dict] | None = None,
) -> MagicMock:
    """Return a mock Supabase client configured for DELETE."""
    mock = MagicMock()
    response = MagicMock()
    response.data = return_data if return_data is not None else [_ENTITY_ROW]
    mock.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = response
    return mock


# ---------------------------------------------------------------------------
# POST /api/v1/entities
# ---------------------------------------------------------------------------


class TestCreateEntity:
    """POST /api/v1/entities tests."""

    def test_create_returns_201_with_entity(self) -> None:
        """AC-1: POST returns 201 with created entity."""
        mock = _supabase_insert_mock()
        client = TestClient(_make_app(mock))

        response = client.post(
            f"{_PREFIX}/entities/",
            json={"title": "Test Entity", "description": "A test"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Entity"
        assert "id" in data
        assert "owner_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_sets_owner_id_from_principal(self) -> None:
        """AC-1: owner_id is set from the authenticated principal, not request body."""
        mock = _supabase_insert_mock()
        client = TestClient(_make_app(mock))

        response = client.post(
            f"{_PREFIX}/entities/",
            json={"title": "Test Entity"},
        )

        assert response.status_code == 201
        # Verify the service was called with the principal's user_id.
        insert_call = mock.table.return_value.insert
        insert_call.assert_called_once()
        payload = insert_call.call_args[0][0]
        assert payload["owner_id"] == _TEST_USER_ID

    def test_create_missing_title_returns_422(self) -> None:
        """AC-8: Missing required title returns 422."""
        client = TestClient(_make_app())

        response = client.post(
            f"{_PREFIX}/entities/",
            json={"description": "no title"},
        )

        assert response.status_code == 422

    def test_create_invalid_json_returns_422_with_details(self) -> None:
        """AC-8: Invalid body returns 422 with details array."""
        client = TestClient(_make_app())

        response = client.post(
            f"{_PREFIX}/entities/",
            json={"title": ""},  # empty string violates min_length=1
        )

        assert response.status_code == 422
        data = response.json()
        assert "details" in data
        assert isinstance(data["details"], list)
        assert len(data["details"]) > 0


# ---------------------------------------------------------------------------
# GET /api/v1/entities
# ---------------------------------------------------------------------------


class TestListEntities:
    """GET /api/v1/entities tests."""

    def test_list_returns_200_with_data_and_count(self) -> None:
        """AC-2: GET returns 200 with data array and count."""
        mock = _supabase_select_list_mock(count=1)
        client = TestClient(_make_app(mock))

        response = client.get(f"{_PREFIX}/entities/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)
        assert data["count"] == 1

    def test_list_uses_default_pagination(self) -> None:
        """AC-2: Defaults to offset=0, limit=20."""
        mock = _supabase_select_list_mock()
        client = TestClient(_make_app(mock))

        client.get(f"{_PREFIX}/entities/")

        # Service computes range(0, 19) for offset=0, limit=20.
        range_call = mock.table.return_value.select.return_value.eq.return_value.range
        range_call.assert_called_once_with(0, 19)

    def test_list_rejects_limit_over_100(self) -> None:
        """AC-9: limit=200 is rejected with 422 by Query(le=100)."""
        client = TestClient(_make_app())

        response = client.get(f"{_PREFIX}/entities/?limit=200")

        assert response.status_code == 422

    def test_list_rejects_negative_offset(self) -> None:
        """Negative offset is rejected with 422 by Query(ge=0)."""
        client = TestClient(_make_app())

        response = client.get(f"{_PREFIX}/entities/?offset=-1")

        assert response.status_code == 422

    def test_list_respects_custom_offset_and_limit(self) -> None:
        """Pagination parameters are forwarded to the service."""
        mock = _supabase_select_list_mock()
        client = TestClient(_make_app(mock))

        client.get(f"{_PREFIX}/entities/?offset=10&limit=5")

        range_call = mock.table.return_value.select.return_value.eq.return_value.range
        range_call.assert_called_once_with(10, 14)


# ---------------------------------------------------------------------------
# GET /api/v1/entities/{entity_id}
# ---------------------------------------------------------------------------


class TestGetEntity:
    """GET /api/v1/entities/{entity_id} tests."""

    def test_get_returns_200_for_owned_entity(self) -> None:
        """AC-3: Returns 200 with entity data for valid owned ID."""
        mock = _supabase_select_single_mock()
        client = TestClient(_make_app(mock))

        response = client.get(f"{_PREFIX}/entities/{_ENTITY_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == _ENTITY_ID
        assert data["owner_id"] == _TEST_USER_ID

    def test_get_nonexistent_returns_404(self) -> None:
        """AC-10: Non-existent UUID returns 404 with ENTITY_NOT_FOUND."""
        mock = _supabase_select_single_mock(raise_api_error=True)
        client = TestClient(_make_app(mock))

        nonexistent_id = str(uuid.uuid4())
        response = client.get(f"{_PREFIX}/entities/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "ENTITY_NOT_FOUND"

    def test_get_non_owned_returns_404(self) -> None:
        """AC-7: Non-owned entity returns 404 (not 403) — service filters by owner_id."""
        mock = _supabase_select_single_mock(raise_api_error=True)
        client = TestClient(_make_app(mock))

        response = client.get(f"{_PREFIX}/entities/{_ENTITY_ID}")

        assert response.status_code == 404
        assert response.json()["code"] == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# PATCH /api/v1/entities/{entity_id}
# ---------------------------------------------------------------------------


class TestUpdateEntity:
    """PATCH /api/v1/entities/{entity_id} tests."""

    def test_patch_updates_provided_fields_only(self) -> None:
        """AC-4: Only patched fields change."""
        updated_row = {**_ENTITY_ROW, "title": "Updated Title"}
        mock = _supabase_update_mock(return_data=[updated_row])
        client = TestClient(_make_app(mock))

        response = client.patch(
            f"{_PREFIX}/entities/{_ENTITY_ID}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == _ENTITY_ROW["description"]

    def test_patch_nonexistent_returns_404(self) -> None:
        """AC-10: PATCH non-existent entity returns 404."""
        mock = MagicMock()
        response_mock = MagicMock()
        response_mock.data = []
        mock.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = response_mock
        client = TestClient(_make_app(mock))

        response = client.patch(
            f"{_PREFIX}/entities/{uuid.uuid4()}",
            json={"title": "Updated"},
        )

        assert response.status_code == 404
        assert response.json()["code"] == "ENTITY_NOT_FOUND"

    def test_patch_empty_body_returns_current_entity(self) -> None:
        """Empty PATCH body is a no-op — returns current entity unchanged."""
        mock = _supabase_select_single_mock()
        client = TestClient(_make_app(mock))

        response = client.patch(
            f"{_PREFIX}/entities/{_ENTITY_ID}",
            json={},
        )

        assert response.status_code == 200
        assert response.json()["title"] == _ENTITY_ROW["title"]


# ---------------------------------------------------------------------------
# DELETE /api/v1/entities/{entity_id}
# ---------------------------------------------------------------------------


class TestDeleteEntity:
    """DELETE /api/v1/entities/{entity_id} tests."""

    def test_delete_returns_204(self) -> None:
        """AC-5: DELETE returns 204 No Content."""
        mock = _supabase_delete_mock()
        client = TestClient(_make_app(mock))

        response = client.delete(f"{_PREFIX}/entities/{_ENTITY_ID}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_nonexistent_returns_404(self) -> None:
        """AC-10: DELETE non-existent entity returns 404."""
        mock = MagicMock()
        response_mock = MagicMock()
        response_mock.data = []
        mock.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = response_mock
        client = TestClient(_make_app(mock))

        response = client.delete(f"{_PREFIX}/entities/{uuid.uuid4()}")

        assert response.status_code == 404
        assert response.json()["code"] == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# Authentication — AC-6
# ---------------------------------------------------------------------------


class TestAuth:
    """Authentication tests: no auth → 401 on all endpoints."""

    @pytest.mark.parametrize(
        "method,path",
        [
            ("POST", f"{_PREFIX}/entities/"),
            ("GET", f"{_PREFIX}/entities/"),
            ("GET", f"{_PREFIX}/entities/{uuid.uuid4()}"),
            ("PATCH", f"{_PREFIX}/entities/{uuid.uuid4()}"),
            ("DELETE", f"{_PREFIX}/entities/{uuid.uuid4()}"),
        ],
    )
    def test_no_auth_returns_401(self, method: str, path: str) -> None:
        """AC-6: All entity endpoints return 401 without authentication."""
        app = _make_app(with_auth=False)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.request(method, path, json={"title": "t"})

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "UNAUTHORIZED"
