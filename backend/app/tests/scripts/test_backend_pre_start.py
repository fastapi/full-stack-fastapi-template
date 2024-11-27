from unittest.mock import MagicMock, patch


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    enter_mock = MagicMock(return_value=True)
    exec_mock = MagicMock(return_value=True)
    enter_mock.configure_mock(**{"exec.return_value": exec_mock})
    session_mock.__enter__.return_value = enter_mock

    with patch("sqlmodel.Session", return_value=session_mock):
        # causing effort if it is not here.. It seams Patch should happen before the import
        from app.backend_pre_start import init

        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."
        session_mock.__enter__.assert_called_once()
        enter_mock.exec.assert_called_once()
