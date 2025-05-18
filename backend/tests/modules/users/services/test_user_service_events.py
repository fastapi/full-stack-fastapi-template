"""
Tests for user service event publishing.
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest

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

    # Create a mock user instead of a real User instance
    user_id = uuid.uuid4()
    user = MagicMock()
    user.id = user_id
    user.email = "test@example.com"
    user.full_name = "Test User"

    repo.create.return_value = user

    return repo, user


def test_create_user_publishes_event(mock_user_repo):
    """Test that creating a user publishes a UserCreatedEvent."""
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

    # Act & Assert
    with patch("app.modules.users.services.user_service.UserCreatedEvent") as mock_event_class:
        mock_event = MagicMock()
        mock_event_class.return_value = mock_event

        # Act
        user_service.create_user(user_create)

        # Assert
        mock_event_class.assert_called_once_with(
            user_id=mock_user.id,
            email=mock_user.email,
            full_name=mock_user.full_name,
        )
        mock_event.publish.assert_called_once()
