"""Unit tests for Entity Pydantic models.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/models/entity.py
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.entity import (
    EntitiesPublic,
    EntityCreate,
    EntityPublic,
    EntityUpdate,
)

# ---------------------------------------------------------------------------
# EntityCreate tests
# ---------------------------------------------------------------------------


def test_entity_create_valid():
    """AC-1: EntityCreate with valid title and description passes validation."""
    entity = EntityCreate(title="Test Entity", description="A test")
    data = entity.model_dump()
    assert data["title"] == "Test Entity"
    assert data["description"] == "A test"


def test_entity_create_missing_title_rejected():
    """EntityCreate without title raises ValidationError (title is required)."""
    with pytest.raises(ValidationError):
        EntityCreate()  # missing required title


def test_entity_create_empty_title_rejected():
    """AC-6: EntityCreate with empty string title raises ValidationError."""
    with pytest.raises(ValidationError):
        EntityCreate(title="")


def test_entity_create_description_optional():
    """EntityCreate without description is valid (description defaults to None)."""
    entity = EntityCreate(title="No Description Entity")
    assert entity.description is None


# ---------------------------------------------------------------------------
# EntityUpdate tests
# ---------------------------------------------------------------------------


def test_entity_update_all_optional():
    """AC-5: EntityUpdate with no fields provided is valid (all fields optional)."""
    update = EntityUpdate()
    assert update.title is None
    assert update.description is None


def test_entity_update_partial():
    """EntityUpdate with only title set serializes correctly."""
    update = EntityUpdate(title="Updated Title")
    data = update.model_dump()
    assert data["title"] == "Updated Title"
    assert data["description"] is None


def test_entity_update_empty_title_rejected():
    """EntityUpdate rejects empty string for title (min_length=1)."""
    with pytest.raises(ValidationError):
        EntityUpdate(title="")


# ---------------------------------------------------------------------------
# EntityPublic tests
# ---------------------------------------------------------------------------


def test_entity_public_includes_all_fields():
    """AC-2: EntityPublic includes id, title, description, owner_id, created_at, updated_at."""
    now = datetime.now(tz=timezone.utc)
    entity_id = uuid4()
    entity = EntityPublic(
        id=entity_id,
        title="Public Entity",
        description="A public entity",
        owner_id="user_abc123",
        created_at=now,
        updated_at=now,
    )
    assert entity.id == entity_id
    assert entity.title == "Public Entity"
    assert entity.description == "A public entity"
    assert entity.owner_id == "user_abc123"
    assert entity.created_at == now
    assert entity.updated_at == now


def test_entity_public_serialization():
    """EntityPublic round-trips through model_dump() preserving all values."""
    now = datetime.now(tz=timezone.utc)
    entity_id = uuid4()
    entity = EntityPublic(
        id=entity_id,
        title="Serialization Test",
        description=None,
        owner_id="user_xyz",
        created_at=now,
        updated_at=now,
    )
    data = entity.model_dump()
    assert data["id"] == entity_id
    assert data["title"] == "Serialization Test"
    assert data["description"] is None
    assert data["owner_id"] == "user_xyz"
    assert data["created_at"] == now
    assert data["updated_at"] == now


# ---------------------------------------------------------------------------
# EntitiesPublic tests
# ---------------------------------------------------------------------------


def test_entities_public_wraps_list():
    """EntitiesPublic(data=[...], count=N) serializes data list and count correctly."""
    now = datetime.now(tz=timezone.utc)
    items = [
        EntityPublic(
            id=uuid4(),
            title=f"Entity {i}",
            description=None,
            owner_id="user_abc",
            created_at=now,
            updated_at=now,
        )
        for i in range(3)
    ]
    collection = EntitiesPublic(data=items, count=3)
    data = collection.model_dump()
    assert data["count"] == 3
    assert len(data["data"]) == 3
    assert data["data"][0]["title"] == "Entity 0"


# ---------------------------------------------------------------------------
# Field constraint tests
# ---------------------------------------------------------------------------


def test_entity_base_title_max_length():
    """title > 255 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        EntityCreate(title="x" * 256)


def test_entity_base_description_max_length():
    """description > 1000 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        EntityCreate(title="Valid Title", description="y" * 1001)


def test_entity_base_title_max_length_boundary():
    """title of exactly 255 characters is valid."""
    entity = EntityCreate(title="a" * 255)
    assert len(entity.title) == 255


def test_entity_base_description_max_length_boundary():
    """description of exactly 1000 characters is valid."""
    entity = EntityCreate(title="Valid Title", description="b" * 1000)
    assert entity.description is not None
    assert len(entity.description) == 1000
