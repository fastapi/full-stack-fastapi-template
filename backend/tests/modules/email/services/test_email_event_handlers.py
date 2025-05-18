"""
Tests for email event handlers.
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.modules.email.services.email_event_handlers import handle_user_created_event
from app.modules.users.domain.events import UserCreatedEvent


@pytest.fixture
def mock_email_service():
    """Fixture for mocked email service."""
    service = MagicMock()
    service.send_new_account_email.return_value = True
    return service


def test_handle_user_created_event(mock_email_service):
    """Test that user created event handler sends welcome email."""
    # Arrange
    user_id = uuid.uuid4()
    email = "test@example.com"
    full_name = "Test User"
    event = UserCreatedEvent(user_id=user_id, email=email, full_name=full_name)
    
    # Act
    with patch("app.modules.email.services.email_event_handlers.get_email_service", 
               return_value=mock_email_service):
        handle_user_created_event(event)
    
    # Assert
    mock_email_service.send_new_account_email.assert_called_once_with(
        email_to=email,
        username=email,  # Using email as username
        password="**********"  # Password is masked in welcome email
    )
