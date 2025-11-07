import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlmodel import select

from app.backend_pre_start import init, logger

pytestmark = pytest.mark.usefixtures('anyio_backend')

async def test_init_successful_connection() -> None:
    engine_mock = AsyncMock()
    # Create a mock that properly handles async context manager
    async_session_mock = AsyncMock()
    async_session_mock.__aenter__.return_value = async_session_mock
    async_session_mock.__aexit__.return_value = None

    select1 = select(1)

    with (
        patch("app.backend_pre_start.AsyncSession", return_value=async_session_mock),
        patch("app.backend_pre_start.select", return_value=select1),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            await init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        async_session_mock.exec.assert_called_once_with(select1)
