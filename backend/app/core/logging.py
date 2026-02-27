"""Structured logging configuration using structlog.

Provides JSON output for production/CI and human-readable console output
for local development, controlled by the LOG_FORMAT setting.

Every log entry includes base fields: timestamp, level, event, service,
version, environment. Request-scoped fields (request_id, correlation_id)
are bound via structlog.contextvars by the request pipeline middleware.
"""

from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any

import structlog


def _add_service_info(
    service: str,
    version: str,
    environment: str,
) -> structlog.types.Processor:
    """Return a processor that injects service metadata into every log entry."""

    def processor(
        _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        event_dict.setdefault("service", service)
        event_dict.setdefault("version", version)
        event_dict.setdefault("environment", environment)
        return event_dict

    return processor


def setup_logging(settings: Any) -> None:
    """Configure structlog with JSON or console rendering.

    Args:
        settings: A settings object with LOG_LEVEL, LOG_FORMAT,
                  SERVICE_NAME, SERVICE_VERSION, and ENVIRONMENT attributes.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_service_info(
            service=settings.SERVICE_NAME,
            version=settings.SERVICE_VERSION,
            environment=settings.ENVIRONMENT,
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.LOG_FORMAT == "console":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
        context_class=dict,
    )


def get_logger(**initial_values: Any) -> Any:
    """Return a structlog bound logger, optionally with initial bound values."""
    return structlog.get_logger(**initial_values)
