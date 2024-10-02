from unittest.mock import Mock, patch

import pytest
from sqlmodel import Session

from app.core.db import init_db
from app.scripts.initial_data import logger, main


def test_init_db_creates_superuser() -> None:
    """
    Test init_db function's superuser creation.

    This test verifies that the init_db function correctly creates a superuser
    with the specified email and password.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail during the test.

    Notes:
        This test uses mock objects to simulate database interactions and
        isolate the functionality being tested.
    """
    # Create a mock session object
    mock_session = Mock(spec=Session)

    # Use multiple patch decorators to mock various dependencies
    with (
        patch("app.scripts.initial_data.Session", return_value=mock_session),
        patch("app.scripts.initial_data.init_db"),
        patch("app.core.db.crud.get_user_by_email", return_value=None) as mock_get_user,
        patch("app.core.db.crud.create_user") as mock_create_user,
        patch("app.core.db.settings") as mock_settings,
    ):
        # Set up mock settings for superuser
        mock_settings.FIRST_SUPERUSER = "test@example.com"
        mock_settings.FIRST_SUPERUSER_PASSWORD = "testpassword"

        # Call the function under test
        init_db(mock_session)

        # Assert that get_user_by_email was called with correct arguments
        mock_get_user.assert_called_once_with(
            session=mock_session, email="test@example.com"
        )
        # Assert that create_user was called
        mock_create_user.assert_called_once()
        # Get the arguments passed to create_user
        create_user_args = mock_create_user.call_args[1]
        # Assert that the correct session was passed
        assert create_user_args["session"] == mock_session
        # Assert that the correct email was used
        assert create_user_args["user_create"].email == "test@example.com"
        # Assert that the correct password was used
        assert create_user_args["user_create"].password == "testpassword"
        # Assert that the user was created as a superuser
        assert create_user_args["user_create"].is_superuser is True


def test_main() -> None:
    """
    Test main function's service initialization.

    This test ensures that the main function successfully initializes the service
    and logs the appropriate messages.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail during the test.

    Notes:
        This test uses mock objects to simulate the initialization process and
        verify the logging behavior.
    """
    # Use patch decorators to mock dependencies
    with (
        patch("app.scripts.initial_data.init") as mock_init,
        patch.object(logger, "info") as mock_logger_info,
    ):
        # Call the function under test
        main()

        # Assert that init was called once
        mock_init.assert_called_once()
        # Assert that logger.info was called twice
        assert mock_logger_info.call_count == 2
        # Assert that the correct log messages were printed
        mock_logger_info.assert_any_call("Creating initial data")
        mock_logger_info.assert_any_call("Initial data created")


if __name__ == "__main__":
    # Run the tests if this script is executed directly
    pytest.main([__file__])
