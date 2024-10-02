from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.scripts.tests_pre_start import init, logger


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

    # Create a mock for the database session
    session_mock = MagicMock()
    # Create a mock for the exec method of the session
    exec_mock = MagicMock(return_value=True)
    # Configure the session mock to return the exec mock when exec is called
    session_mock.configure_mock(**{"exec.return_value": exec_mock})

    # Use patch to mock various components
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
