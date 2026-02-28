"""Unit tests for FastAPI lifespan startup/shutdown sequence.

Verifies AC-10: shutdown order is log event → close http_client → sentry flush.

Uses no database or external dependencies. Run with:
  uv run pytest backend/tests/unit/test_lifespan.py -v
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


class TestLifespanShutdownOrder:
    """Shutdown sequence: log → close http_client → sentry flush (AC-10)."""

    def test_shutdown_order_log_then_close_then_flush(self) -> None:
        """Shutdown calls happen in exact order: logger.info, http_client.close, sentry flush."""
        call_order: list[str] = []

        mock_http_client = AsyncMock()
        mock_http_client.close = AsyncMock(
            side_effect=lambda: call_order.append("http_close")
        )

        with (
            patch("app.main.create_supabase_client", return_value=MagicMock()),
            patch("app.main.HttpClient", return_value=mock_http_client),
            patch("app.main.logger") as mock_logger,
            patch("app.main.sentry_sdk") as mock_sentry,
        ):
            # Track call order via side_effects
            def log_info(event: str, **_kwargs: object) -> None:
                if event == "app_shutdown":
                    call_order.append("log_shutdown")

            mock_logger.info = MagicMock(side_effect=log_info)
            mock_sentry.flush = MagicMock(
                side_effect=lambda **kw: call_order.append("sentry_flush")
            )

            with TestClient(app):
                pass  # startup runs; exiting triggers shutdown

        assert call_order == ["log_shutdown", "http_close", "sentry_flush"]

    def test_shutdown_closes_http_client_even_after_log(self) -> None:
        """http_client.close() is still called after the shutdown log event."""
        mock_http_client = AsyncMock()

        with (
            patch("app.main.create_supabase_client", return_value=MagicMock()),
            patch("app.main.HttpClient", return_value=mock_http_client),
            patch("app.main.logger"),
            patch("app.main.sentry_sdk"),
        ):
            with TestClient(app):
                pass

        mock_http_client.close.assert_awaited_once()

    def test_sentry_flush_called_with_timeout(self) -> None:
        """sentry_sdk.flush(timeout=2.0) is called during shutdown."""
        mock_http_client = AsyncMock()

        with (
            patch("app.main.create_supabase_client", return_value=MagicMock()),
            patch("app.main.HttpClient", return_value=mock_http_client),
            patch("app.main.logger"),
            patch("app.main.sentry_sdk") as mock_sentry,
        ):
            with TestClient(app):
                pass

        mock_sentry.flush.assert_called_once_with(timeout=2.0)
