"""
Tests for the event system.

This module tests the core event system functionality.
"""
import asyncio
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from app.core.events import (
    EventBase,
    event_handler,
    publish_event,
    subscribe_to_event,
    unsubscribe_from_event,
)


# Sample event classes for testing - not actual test classes
class SampleEvent(EventBase):
    """Sample event class for testing."""
    event_type: str = "test.event"
    data: str


class SampleEventWithPayload(EventBase):
    """Sample event with additional payload for testing."""
    event_type: str = "test.event.payload"
    id: int
    name: str
    details: dict


def test_event_base_initialization():
    """Test EventBase initialization."""
    # Arrange & Act
    event = SampleEvent(data="test data")

    # Assert
    assert event.event_type == "test.event"
    assert event.data == "test data"
    assert isinstance(event, EventBase)
    assert isinstance(event, BaseModel)


def test_event_with_payload_initialization():
    """Test event with payload initialization."""
    # Arrange & Act
    event = SampleEventWithPayload(
        id=1,
        name="test",
        details={"key": "value"}
    )

    # Assert
    assert event.event_type == "test.event.payload"
    assert event.id == 1
    assert event.name == "test"
    assert event.details == {"key": "value"}


def test_subscribe_and_publish_event():
    """Test subscribing to and publishing an event."""
    # Arrange
    mock_handler = MagicMock()
    mock_handler.__name__ = "mock_handler"  # Add __name__ attribute
    event = SampleEvent(data="test data")

    # Act
    subscribe_to_event("test.event", mock_handler)
    publish_event(event)

    # Assert
    mock_handler.assert_called_once_with(event)

    # Cleanup
    unsubscribe_from_event("test.event", mock_handler)


def test_unsubscribe_from_event():
    """Test unsubscribing from an event."""
    # Arrange
    mock_handler = MagicMock()
    mock_handler.__name__ = "mock_handler"  # Add __name__ attribute
    event = SampleEvent(data="test data")
    subscribe_to_event("test.event", mock_handler)

    # Act
    unsubscribe_from_event("test.event", mock_handler)
    publish_event(event)

    # Assert
    mock_handler.assert_not_called()


def test_multiple_handlers_for_event():
    """Test multiple handlers for the same event."""
    # Arrange
    mock_handler1 = MagicMock()
    mock_handler1.__name__ = "mock_handler1"  # Add __name__ attribute
    mock_handler2 = MagicMock()
    mock_handler2.__name__ = "mock_handler2"  # Add __name__ attribute
    event = SampleEvent(data="test data")

    # Act
    subscribe_to_event("test.event", mock_handler1)
    subscribe_to_event("test.event", mock_handler2)
    publish_event(event)

    # Assert
    mock_handler1.assert_called_once_with(event)
    mock_handler2.assert_called_once_with(event)

    # Cleanup
    unsubscribe_from_event("test.event", mock_handler1)
    unsubscribe_from_event("test.event", mock_handler2)


def test_event_handler_decorator():
    """Test event_handler decorator."""
    # Arrange
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"  # Add __name__ attribute

    # Act
    # We need to use the decorated function to avoid linting warnings
    decorated_function = event_handler("test.event")(mock_function)
    assert decorated_function == mock_function  # Verify decorator returns original function

    event = SampleEvent(data="test data")
    publish_event(event)

    # Assert
    mock_function.assert_called_once_with(event)

    # Cleanup
    unsubscribe_from_event("test.event", mock_function)


@pytest.mark.anyio(backends=["asyncio"])
async def test_async_event_handler():
    """Test async event handler."""
    # Arrange
    result = []

    async def async_handler(event):
        await asyncio.sleep(0.1)
        result.append(event.data)

    event = SampleEvent(data="async test")

    # Act
    subscribe_to_event("test.event", async_handler)
    publish_event(event)

    # Wait for async handler to complete
    await asyncio.sleep(0.2)

    # Assert
    assert result == ["async test"]

    # Cleanup
    unsubscribe_from_event("test.event", async_handler)


def test_error_in_handler_doesnt_affect_others():
    """Test that an error in one handler doesn't affect others."""
    # Arrange
    # Use a named function to avoid linting warnings about unused parameters
    def failing_handler(_):
        """Handler that always fails."""
        raise Exception("Test exception")

    success_handler = MagicMock()
    success_handler.__name__ = "success_handler"  # Add __name__ attribute
    event = SampleEvent(data="test data")

    # Act
    subscribe_to_event("test.event", failing_handler)
    subscribe_to_event("test.event", success_handler)

    with patch("app.core.events.logger") as mock_logger:
        publish_event(event)

    # Assert
    success_handler.assert_called_once_with(event)
    mock_logger.exception.assert_called_once()

    # Cleanup
    unsubscribe_from_event("test.event", failing_handler)
    unsubscribe_from_event("test.event", success_handler)


def test_publish_event_with_no_handlers():
    """Test publishing an event with no handlers."""
    # Arrange
    event = SampleEventWithPayload(id=1, name="test", details={})

    # Act & Assert (should not raise any exceptions)
    with patch("app.core.events.logger") as mock_logger:
        publish_event(event)

    # Verify debug log was called
    mock_logger.debug.assert_called_once()
