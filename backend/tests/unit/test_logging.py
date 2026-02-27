"""Unit tests for structured logging configuration.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/logging.py

Uses no database or external dependencies. Run with:
  uv run pytest backend/tests/unit/test_logging.py -v
"""

import io
import json

import structlog

from app.core.logging import get_logger, setup_logging

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal settings-like object for setup_logging."""

    class _FakeSettings:
        LOG_LEVEL: str = overrides.get("LOG_LEVEL", "INFO")
        LOG_FORMAT: str = overrides.get("LOG_FORMAT", "json")
        SERVICE_NAME: str = overrides.get("SERVICE_NAME", "test-service")
        SERVICE_VERSION: str = overrides.get("SERVICE_VERSION", "0.0.1")
        ENVIRONMENT: str = overrides.get("ENVIRONMENT", "local")

    return _FakeSettings()


# ---------------------------------------------------------------------------
# Tests: setup_logging
# ---------------------------------------------------------------------------


def test_setup_logging_returns_none():
    """setup_logging() is callable and returns None."""
    settings = _make_settings()
    result = setup_logging(settings)
    assert result is None


def test_json_format_produces_valid_json():
    """LOG_FORMAT=json produces valid JSON log output."""
    settings = _make_settings(LOG_FORMAT="json")
    setup_logging(settings)

    buf = io.StringIO()
    structlog.configure(
        **{**structlog.get_config(), "logger_factory": structlog.PrintLoggerFactory(file=buf)}
    )
    logger = structlog.get_logger()
    logger.info("test_event", key="value")

    output = buf.getvalue().strip()
    parsed = json.loads(output)
    assert parsed["event"] == "test_event"
    assert parsed["key"] == "value"


def test_console_format_produces_readable_text():
    """LOG_FORMAT=console produces non-JSON human-readable output."""
    settings = _make_settings(LOG_FORMAT="console")
    setup_logging(settings)

    buf = io.StringIO()
    structlog.configure(
        **{**structlog.get_config(), "logger_factory": structlog.PrintLoggerFactory(file=buf)}
    )
    logger = structlog.get_logger()
    logger.info("hello_console")

    output = buf.getvalue().strip()
    # Console output should NOT be valid JSON
    with __import__("pytest").raises(json.JSONDecodeError):
        json.loads(output)
    # But should contain the event name
    assert "hello_console" in output


def test_base_fields_present_in_json():
    """JSON log includes all required base fields: timestamp, level, event, service, version, environment."""
    settings = _make_settings(
        LOG_FORMAT="json",
        SERVICE_NAME="my-svc",
        SERVICE_VERSION="1.2.3",
        ENVIRONMENT="staging",
    )
    setup_logging(settings)

    buf = io.StringIO()
    structlog.configure(
        **{**structlog.get_config(), "logger_factory": structlog.PrintLoggerFactory(file=buf)}
    )
    logger = structlog.get_logger()
    logger.info("test_fields")

    parsed = json.loads(buf.getvalue().strip())
    assert "timestamp" in parsed
    assert parsed["level"] == "info"
    assert parsed["event"] == "test_fields"
    assert parsed["service"] == "my-svc"
    assert parsed["version"] == "1.2.3"
    assert parsed["environment"] == "staging"


def test_log_level_filtering():
    """DEBUG messages are filtered when LOG_LEVEL=INFO."""
    settings = _make_settings(LOG_FORMAT="json", LOG_LEVEL="INFO")
    setup_logging(settings)

    buf = io.StringIO()
    structlog.configure(
        **{**structlog.get_config(), "logger_factory": structlog.PrintLoggerFactory(file=buf)}
    )
    logger = structlog.get_logger()
    logger.debug("should_not_appear")

    output = buf.getvalue().strip()
    assert output == ""


def test_get_logger_returns_bound_logger():
    """get_logger() returns a structlog BoundLogger instance."""
    settings = _make_settings()
    setup_logging(settings)

    logger = get_logger()
    # Should have standard log methods
    assert callable(getattr(logger, "info", None))
    assert callable(getattr(logger, "warning", None))
    assert callable(getattr(logger, "error", None))
    assert callable(getattr(logger, "debug", None))
