"""Unit tests for Entity service layer.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/services/entity_service.py

All Supabase client interactions are mocked via ``unittest.mock.MagicMock``
so no live database connection is required.
"""

from unittest.mock import MagicMock

import pytest
from postgrest.exceptions import APIError

from app.core.errors import ServiceError
from app.models.entity import EntityCreate, EntityUpdate
from app.services.entity_service import (
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    update_entity,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

ENTITY_ID = "550e8400-e29b-41d4-a716-446655440000"
OWNER_ID = "user_abc123"
CREATED_AT = "2026-02-28T00:00:00+00:00"
UPDATED_AT = "2026-02-28T00:00:00+00:00"

ENTITY_RECORD = {
    "id": ENTITY_ID,
    "title": "Test Entity",
    "description": "A test",
    "owner_id": OWNER_ID,
    "created_at": CREATED_AT,
    "updated_at": UPDATED_AT,
}


def make_mock_supabase() -> MagicMock:
    """Create a fresh mock Supabase client with chainable table builder."""
    return MagicMock()


# ---------------------------------------------------------------------------
# Happy Path: create_entity
# ---------------------------------------------------------------------------


def test_create_entity_inserts_and_returns():
    """AC-3: create_entity inserts a new row and returns a populated EntityPublic."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = [ENTITY_RECORD]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = (
        mock_response
    )

    data = EntityCreate(title="Test Entity", description="A test")
    result = create_entity(mock_supabase, data, OWNER_ID)

    assert result.title == "Test Entity"
    assert result.description == "A test"
    assert result.owner_id == OWNER_ID
    assert str(result.id) == ENTITY_ID


def test_create_entity_calls_insert_with_correct_payload():
    """create_entity passes title, description, and owner_id to supabase insert."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = [ENTITY_RECORD]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = (
        mock_response
    )

    data = EntityCreate(title="Test Entity", description="A test")
    create_entity(mock_supabase, data, OWNER_ID)

    mock_supabase.table.assert_called_with("entities")
    call_args = mock_supabase.table.return_value.insert.call_args
    payload = call_args[0][0]
    assert payload["title"] == "Test Entity"
    assert payload["description"] == "A test"
    assert payload["owner_id"] == OWNER_ID


def test_create_entity_empty_response_raises_500():
    """create_entity raises ServiceError(500) when insert returns empty data (e.g. RLS block)."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase.table.return_value.insert.return_value.execute.return_value = (
        mock_response
    )

    data = EntityCreate(title="Test Entity", description="A test")
    with pytest.raises(ServiceError) as exc_info:
        create_entity(mock_supabase, data, OWNER_ID)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_CREATE_FAILED"


# ---------------------------------------------------------------------------
# Happy Path: get_entity
# ---------------------------------------------------------------------------


def test_get_entity_success():
    """get_entity returns EntityPublic when entity exists and is owned by the caller."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = ENTITY_RECORD
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value
    ) = mock_response

    result = get_entity(mock_supabase, ENTITY_ID, OWNER_ID)

    assert str(result.id) == ENTITY_ID
    assert result.title == "Test Entity"
    assert result.owner_id == OWNER_ID


# ---------------------------------------------------------------------------
# Happy Path: list_entities
# ---------------------------------------------------------------------------


def test_list_entities_paginated():
    """list_entities returns EntitiesPublic with data list and total count."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = [ENTITY_RECORD]
    mock_response.count = 1
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value
    ) = mock_response

    result = list_entities(mock_supabase, OWNER_ID, offset=0, limit=20)

    assert result.count == 1
    assert len(result.data) == 1
    assert result.data[0].title == "Test Entity"


def test_list_entities_default_pagination():
    """list_entities uses offset=0 and limit=20 when called with defaults."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value
    ) = mock_response

    list_entities(mock_supabase, OWNER_ID)

    # Verify .range() was called with default offset=0 and limit=20 → range(0, 19)
    range_call = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range
    )
    range_call.assert_called_once_with(0, 19)


# ---------------------------------------------------------------------------
# Happy Path: update_entity
# ---------------------------------------------------------------------------


def test_update_entity_success():
    """update_entity applies the update payload and returns the updated EntityPublic."""
    mock_supabase = make_mock_supabase()

    updated_record = {**ENTITY_RECORD, "title": "Updated Title"}
    mock_response = MagicMock()
    mock_response.data = [updated_record]
    (
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value
    ) = mock_response

    data = EntityUpdate(title="Updated Title")
    result = update_entity(mock_supabase, ENTITY_ID, OWNER_ID, data)

    assert result.title == "Updated Title"
    assert str(result.id) == ENTITY_ID


# ---------------------------------------------------------------------------
# Happy Path: delete_entity
# ---------------------------------------------------------------------------


def test_delete_entity_success():
    """delete_entity succeeds and returns None when entity exists and is owned."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = [ENTITY_RECORD]
    (
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value
    ) = mock_response

    # Should not raise
    result = delete_entity(mock_supabase, ENTITY_ID, OWNER_ID)
    assert result is None


# ---------------------------------------------------------------------------
# Edge Case: get_entity not found
# ---------------------------------------------------------------------------


def test_get_entity_not_found_raises_404():
    """AC-7: get_entity raises ServiceError(404) when the entity does not exist.

    supabase-py raises APIError with code PGRST116 when .single() matches zero rows.
    """
    mock_supabase = make_mock_supabase()

    api_error = APIError({"message": "JSON object requested, multiple (or no) rows returned", "code": "PGRST116", "details": "", "hint": ""})
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect
    ) = api_error

    with pytest.raises(ServiceError) as exc_info:
        get_entity(mock_supabase, ENTITY_ID, OWNER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# Edge Case: list_entities limit capping
# ---------------------------------------------------------------------------


def test_list_entities_caps_limit_at_100():
    """AC-8: list_entities caps limit at 100 even when a larger value is passed."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value
    ) = mock_response

    list_entities(mock_supabase, OWNER_ID, offset=0, limit=200)

    # With limit capped at 100 and offset=0 → range(0, 99)
    range_call = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range
    )
    range_call.assert_called_once_with(0, 99)


def test_list_entities_clamps_negative_offset():
    """list_entities clamps negative offset to 0."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value
    ) = mock_response

    list_entities(mock_supabase, OWNER_ID, offset=-5, limit=10)

    range_call = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range
    )
    # offset clamped to 0, limit=10 → range(0, 9)
    range_call.assert_called_once_with(0, 9)


def test_list_entities_clamps_zero_limit_to_one():
    """list_entities clamps limit=0 to 1 to avoid invalid range."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value
    ) = mock_response

    list_entities(mock_supabase, OWNER_ID, offset=0, limit=0)

    range_call = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range
    )
    # limit clamped to 1 → range(0, 0)
    range_call.assert_called_once_with(0, 0)


# ---------------------------------------------------------------------------
# Edge Case: update_entity not found
# ---------------------------------------------------------------------------


def test_update_entity_not_found():
    """update_entity raises ServiceError(404) when update returns empty data."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    (
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value
    ) = mock_response

    data = EntityUpdate(title="New Title")
    with pytest.raises(ServiceError) as exc_info:
        update_entity(mock_supabase, ENTITY_ID, OWNER_ID, data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# Edge Case: delete_entity not found
# ---------------------------------------------------------------------------


def test_delete_entity_not_found():
    """delete_entity raises ServiceError(404) when delete returns empty data."""
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = []
    (
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value
    ) = mock_response

    with pytest.raises(ServiceError) as exc_info:
        delete_entity(mock_supabase, ENTITY_ID, OWNER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# Error Handling: supabase errors propagate as ServiceError
# ---------------------------------------------------------------------------


def test_create_entity_supabase_error_raises_service_error():
    """AC-9: create_entity raises ServiceError(500) when supabase raises an exception."""
    mock_supabase = make_mock_supabase()

    mock_supabase.table.return_value.insert.return_value.execute.side_effect = (
        Exception("DB connection error")
    )

    data = EntityCreate(title="Test Entity")
    with pytest.raises(ServiceError) as exc_info:
        create_entity(mock_supabase, data, OWNER_ID)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_CREATE_FAILED"


def test_get_entity_infrastructure_error_raises_500():
    """AC-10: generic infrastructure errors in get_entity raise ServiceError(500).

    Non-APIError exceptions (network failures, timeouts) are distinguished from
    not-found (APIError) and correctly reported as 500 server errors.
    """
    mock_supabase = make_mock_supabase()

    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect
    ) = Exception("Connection refused")

    with pytest.raises(ServiceError) as exc_info:
        get_entity(mock_supabase, ENTITY_ID, OWNER_ID)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_GET_FAILED"


def test_list_entities_supabase_error_raises_service_error():
    """list_entities raises ServiceError(500) when supabase raises an exception."""
    mock_supabase = make_mock_supabase()

    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.range.return_value.execute.side_effect
    ) = Exception("Query timeout")

    with pytest.raises(ServiceError) as exc_info:
        list_entities(mock_supabase, OWNER_ID)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_LIST_FAILED"


def test_update_entity_supabase_error_raises_service_error():
    """update_entity raises ServiceError(500) when supabase raises an unexpected exception."""
    mock_supabase = make_mock_supabase()

    (
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.side_effect
    ) = Exception("DB connection error")

    data = EntityUpdate(title="New Title")
    with pytest.raises(ServiceError) as exc_info:
        update_entity(mock_supabase, ENTITY_ID, OWNER_ID, data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_UPDATE_FAILED"


def test_delete_entity_supabase_error_raises_service_error():
    """delete_entity raises ServiceError(500) when supabase raises an unexpected exception."""
    mock_supabase = make_mock_supabase()

    (
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.side_effect
    ) = Exception("DB connection error")

    with pytest.raises(ServiceError) as exc_info:
        delete_entity(mock_supabase, ENTITY_ID, OWNER_ID)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "ENTITY_DELETE_FAILED"


# ---------------------------------------------------------------------------
# Edge Case: update_entity no fields to update
# ---------------------------------------------------------------------------


def test_update_entity_no_fields_to_update():
    """AC-5 service-level: EntityUpdate() with no fields fetches and returns current entity.

    When no fields are provided, the service skips the update and falls back to
    fetching the current entity via get_entity (select + single).
    """
    mock_supabase = make_mock_supabase()

    mock_response = MagicMock()
    mock_response.data = ENTITY_RECORD
    (
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value
    ) = mock_response

    data = EntityUpdate()  # no fields set
    result = update_entity(mock_supabase, ENTITY_ID, OWNER_ID, data)

    # Should return the existing entity without calling update
    mock_supabase.table.return_value.update.assert_not_called()
    assert str(result.id) == ENTITY_ID
    assert result.title == "Test Entity"
