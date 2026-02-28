"""Clerk JWT authentication dependency.

Provides get_current_principal(), a FastAPI dependency that validates the
Bearer token in the Authorization header using the Clerk SDK and returns
the authenticated Principal.

Error codes:
  AUTH_MISSING_TOKEN   — no session token in request
  AUTH_EXPIRED_TOKEN   — token has expired
  AUTH_INVALID_TOKEN   — signature bad, wrong party, or other failure
"""

from typing import Any

import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import (
    AuthenticateRequestOptions,
    AuthErrorReason,
    TokenVerificationErrorReason,
)
from fastapi import Request

from app.core.errors import ServiceError
from app.models.auth import Principal


def _get_clerk_sdk() -> Clerk:
    """Return a Clerk SDK instance initialised with the current secret key.

    Deferred import of settings avoids module-level instantiation failure
    during tests where the real environment is not set up.
    """
    from app.core.config import settings

    return Clerk(bearer_auth=settings.CLERK_SECRET_KEY.get_secret_value())


def _get_authorized_parties() -> list[str]:
    """Return the configured list of authorized parties.

    Deferred import keeps settings out of module-level scope.
    """
    from app.core.config import settings

    return settings.CLERK_AUTHORIZED_PARTIES


def _convert_request(request: Request) -> httpx.Request:
    """Convert a FastAPI/Starlette Request to an httpx.Request for the Clerk SDK."""
    return httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )


def _map_error_reason(reason: Any) -> tuple[str, str]:
    """Map a Clerk error reason to (message, error_code).

    Returns a (message, code) tuple suitable for ServiceError.
    """
    if reason is AuthErrorReason.SESSION_TOKEN_MISSING:
        return ("Missing authentication token", "AUTH_MISSING_TOKEN")
    if reason is TokenVerificationErrorReason.TOKEN_EXPIRED:
        return ("Token expired", "AUTH_EXPIRED_TOKEN")
    if reason is TokenVerificationErrorReason.TOKEN_INVALID_SIGNATURE:
        return ("Invalid token signature", "AUTH_INVALID_TOKEN")
    if reason is TokenVerificationErrorReason.TOKEN_INVALID_AUTHORIZED_PARTIES:
        return ("Token not from authorized party", "AUTH_INVALID_TOKEN")
    return ("Authentication failed", "AUTH_INVALID_TOKEN")


def _extract_roles(payload: dict[str, Any]) -> list[str]:
    """Extract roles from the Clerk JWT payload.

    Clerk encodes the active organisation role under the 'o' claim:
      payload["o"]["rol"]  -> e.g. "org:admin"

    Falls back to an empty list when the user has no active organisation
    or the claim is absent.
    """
    org_data = payload.get("o")
    if not isinstance(org_data, dict):
        return []
    role = org_data.get("rol")
    if not role:
        return []
    return [role] if isinstance(role, str) else list(role)


async def get_current_principal(request: Request) -> Principal:
    """FastAPI dependency: validate the Clerk session token and return Principal.

    Raises:
        ServiceError(401, ...) for any authentication failure.
    """
    try:
        httpx_request = _convert_request(request)
        options = AuthenticateRequestOptions(
            authorized_parties=_get_authorized_parties(),
        )
        request_state = _get_clerk_sdk().authenticate_request(httpx_request, options)
    except Exception as exc:
        raise ServiceError(
            status_code=401,
            message="Authentication failed",
            code="AUTH_INVALID_TOKEN",
        ) from exc

    if not request_state.is_signed_in:
        message, code = _map_error_reason(request_state.reason)
        raise ServiceError(status_code=401, message=message, code=code)

    payload: dict[str, Any] = request_state.payload or {}

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    if not user_id or not session_id:
        raise ServiceError(
            status_code=401,
            message="Authentication failed",
            code="AUTH_INVALID_TOKEN",
        )

    principal = Principal(
        user_id=user_id,
        session_id=session_id,
        org_id=payload.get("org_id"),
        roles=_extract_roles(payload),
    )

    # Store user_id on request state so logging middleware can include it.
    request.state.user_id = principal.user_id

    return principal
