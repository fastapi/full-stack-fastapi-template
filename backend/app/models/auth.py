"""Authentication principal model.

Represents the authenticated caller extracted from a validated JWT.
Used as a dependency injection type throughout API route handlers.
"""

from pydantic import BaseModel


class Principal(BaseModel):
    """Authenticated user principal extracted from Clerk JWT."""

    user_id: str
    """Clerk user ID (e.g. 'user_2abc...')."""

    roles: list[str] = []
    """List of role names granted to this user. Defaults to empty list."""

    org_id: str | None = None
    """Clerk organisation ID, or None when user has no active organisation."""
