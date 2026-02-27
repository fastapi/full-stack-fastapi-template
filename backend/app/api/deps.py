"""Typed FastAPI dependency declarations.

All cross-cutting concerns (database, auth, HTTP client, request context) are
injected via ``Annotated[T, Depends(...)]`` types.  Route handlers declare what
they need through parameter type annotations and FastAPI resolves the
dependency chain automatically.

Every dependency listed here is overridable in tests via
``app.dependency_overrides[fn] = mock_fn``.
"""

from typing import Annotated

from fastapi import Depends, Request
from supabase import Client as SupabaseClient

from app.core.auth import get_current_principal
from app.core.http_client import HttpClient, get_http_client
from app.core.supabase import get_supabase
from app.models.auth import Principal


def get_request_id(request: Request) -> str:
    """Return the current request ID from request state.

    The request_id is set by RequestPipelineMiddleware on every request.
    Falls back to an empty string if middleware has not run (e.g. in tests).
    """
    return getattr(request.state, "request_id", "")


SupabaseDep = Annotated[SupabaseClient, Depends(get_supabase)]
"""Supabase client instance, initialised at app startup."""

PrincipalDep = Annotated[Principal, Depends(get_current_principal)]
"""Authenticated user principal extracted from Clerk JWT."""

HttpClientDep = Annotated[HttpClient, Depends(get_http_client)]
"""Shared async HTTP client with retry, circuit breaker, header propagation."""

RequestIdDep = Annotated[str, Depends(get_request_id)]
"""Current request UUID from the request pipeline middleware."""
