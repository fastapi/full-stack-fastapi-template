from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.backend_pre_start import init, logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_cm = MagicMock()
    session = session_cm.__enter__.return_value
    session.exec.return_value = True

    with (
        patch("sqlmodel.Session", return_value=session_cm),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        init(engine_mock)

        session.exec.assert_called_once_with(select(1))
