"""
Integration tests for user and email modules.

This module tests the integration between the user and email modules
via the event system.
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app.modules.email.services.email_event_handlers import handle_user_created_event
from app.modules.users.domain.events import UserCreatedEvent
from app.modules.users.domain.models import UserCreate
from app.modules.users.repository.user_repo import UserRepository
from app.modules.users.services.user_service import UserService


@pytest.fixture
def mock_user_repo():
    """Fixture for mocked user repository."""
    repo = MagicMock(spec=UserRepository)

    # Mock the exists_by_email method to return False (user doesn't exist)
    repo.exists_by_email.return_value = False

    # Create a mock user with a fixed UUID for testing
    user_id = uuid.uuid4()
    user = MagicMock()
    user.id = user_id
    user.email = "test@example.com"
    user.full_name = "Test User"

    # Mock the create method to return the user
    repo.create.return_value = user

    return repo, user


@pytest.fixture
def mock_email_service():
    """Fixture for mocked email service."""
    service = MagicMock()
    service.send_new_account_email.return_value = True
    return service


def test_user_creation_triggers_email_via_event(mock_user_repo, mock_email_service):
    """
    Test that creating a user triggers an email via the event system.

    This is an integration test that verifies the event flow from
    user creation to email sending.
    """
    # Arrange
    mock_repo, mock_user = mock_user_repo
    user_service = UserService(mock_repo)

    user_create = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
        is_superuser=False,
        is_active=True,
    )

    # Mock the event publishing to capture the event
    with patch("app.modules.users.domain.events.publish_event") as mock_publish:
        # Act - Create the user
        user_service.create_user(user_create)

        # Assert - Verify event was published
        mock_publish.assert_called_once()

        # Get the published event
        event = mock_publish.call_args[0][0]
        assert isinstance(event, UserCreatedEvent)
        assert event.user_id == mock_user.id
        assert event.email == mock_user.email
        assert event.full_name == mock_user.full_name

        # Now test that the email handler processes this event correctly
        with patch("app.modules.email.services.email_event_handlers.get_email_service",
                   return_value=mock_email_service):
            # Act - Handle the event
            handle_user_created_event(event)

            # Assert - Verify email was sent
            mock_email_service.send_new_account_email.assert_called_once_with(
                email_to=mock_user.email,
                username=mock_user.email,
                password="**********"
            )
