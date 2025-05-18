"""
Tests for user domain events.
"""
import uuid
from unittest.mock import patch

import pytest

from app.core.events import EventBase
from app.modules.users.domain.events import UserCreatedEvent
from app.modules.users.domain.models import UserPublic


def test_user_created_event_init():
    """Test UserCreatedEvent initialization."""
    # Arrange
    user_id = uuid.uuid4()
    email = "test@example.com"

    # Act
    event = UserCreatedEvent(user_id=user_id, email=email)

    # Assert
    assert event.event_type == "user.created"
    assert event.user_id == user_id
    assert event.email == email
    assert isinstance(event, EventBase)


def test_user_created_event_publish():
    """Test UserCreatedEvent publish method."""
    # Arrange
    user_id = uuid.uuid4()
    email = "test@example.com"
    event = UserCreatedEvent(user_id=user_id, email=email)

    # Act
    with patch("app.modules.users.domain.events.publish_event") as mock_publish_event:
        event.publish()

        # Assert
        mock_publish_event.assert_called_once_with(event)
