from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from app.backend_pre_start import init
from app.core.db import engine


class TestBackendPreStart:
    @pytest.fixture
    @staticmethod
    def mock_session() -> Generator[MagicMock, None, None]:
        with patch("app.backend_pre_start.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value.__enter__.return_value = mock_session
            mock_session.exec.return_value = True
            yield mock_session

    def test_init_function(self, mock_session: MagicMock) -> None:
        init(engine)
        mock_session.exec.assert_called_once()
