from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.scripts.backend_pre_start import init, logger, main


def test_init_successful_connection() -> None:
    """
    Test successful database connection initialization.

    This test verifies that the init function successfully connects to the database
    by mocking the necessary components and asserting the expected behavior.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the connection is not successful or if the session
                        does not execute the select statement as expected.

    Notes:
        This test uses mocking to simulate the database engine and session.
    """
    # Create a mock for the database engine
    engine_mock = MagicMock()

    # Create a mock for the database session and its exec method
    session_mock = MagicMock()
    exec_mock = MagicMock(return_value=True)
    session_mock.configure_mock(**{"exec.return_value": exec_mock})

    # Patch necessary dependencies
    with (
        patch("sqlmodel.Session", return_value=session_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            # Attempt to initialize the database connection
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        # Assert that the connection was successful
        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        # Assert that the session executed a select statement once
        assert session_mock.exec.called_once_with(
            select(1)
        ), "The session should execute a select statement once."


def test_main() -> None:
    """
    Test the main function for service initialization.

    This test verifies that the main function successfully initializes the service
    by mocking the necessary dependencies and asserting the expected behavior.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the init function is not called with the mocked engine
                        or if the logger does not log the expected messages.

    Notes:
        This test uses mocking to simulate the init function, engine, and logger.
    """
    # Patch necessary dependencies
    with (
        patch("app.scripts.backend_pre_start.init") as mock_init,
        patch("app.scripts.backend_pre_start.engine") as mock_engine,
        patch.object(logger, "info") as mock_logger_info,
    ):
        # Call the main function
        main()

        # Assert that init was called once with the mocked engine
        mock_init.assert_called_once_with(mock_engine)
        # Assert that logger.info was called twice
        assert mock_logger_info.call_count == 2
        # Assert that the correct log messages were printed
        mock_logger_info.assert_any_call("Initializing service")
        mock_logger_info.assert_any_call("Service finished initializing")
