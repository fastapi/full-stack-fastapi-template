"""Supabase client initialization and FastAPI dependency.

Provides:
  - create_supabase_client: factory function that initializes a Supabase Client
  - get_supabase: FastAPI dependency that retrieves the client from app.state
"""

from typing import cast

import supabase
from fastapi import Request
from supabase import Client

from app.core.errors import ServiceError
from app.core.logging import get_logger

logger = get_logger(module=__name__)


def create_supabase_client(url: str, key: str) -> Client:
    """Initialize and return a Supabase Client.

    Args:
        url: The Supabase project URL (string form).
        key: The Supabase service key.

    Returns:
        An initialized supabase.Client instance.

    Raises:
        ServiceError: 503 SERVICE_UNAVAILABLE if the client cannot be created.
    """
    try:
        client = supabase.create_client(url, key)
        logger.info("supabase_client_initialized", url=url)
        return client
    except Exception as exc:
        logger.error("supabase_client_init_failed", url=url, error=str(exc))
        raise ServiceError(
            status_code=503,
            message="Failed to initialize Supabase client",
            code="SERVICE_UNAVAILABLE",
        ) from exc


def get_supabase(request: Request) -> Client:
    """FastAPI dependency — return the Supabase Client from app.state.

    Expects the client to be stored at ``request.app.state.supabase`` during
    application startup (e.g. in a lifespan handler).

    Raises:
        ServiceError: 503 SERVICE_UNAVAILABLE if the client is not initialized.
    """
    try:
        return cast(Client, request.app.state.supabase)
    except AttributeError as exc:
        logger.error("supabase_client_not_found_in_app_state")
        raise ServiceError(
            status_code=503,
            message="Supabase client not initialized",
            code="SERVICE_UNAVAILABLE",
        ) from exc
