"""
Auth domain models.

This module contains domain models related to authentication and authorization.
"""
from typing import Optional

from pydantic import Field
from sqlmodel import SQLModel


class TokenPayload(SQLModel):
    """Contents of JWT token."""
    sub: Optional[str] = None


class Token(SQLModel):
    """JSON payload containing access token."""
    access_token: str
    token_type: str = "bearer"


class NewPassword(SQLModel):
    """Model for password reset."""
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class PasswordReset(SQLModel):
    """Model for requesting a password reset."""
    email: str


class LoginRequest(SQLModel):
    """Request model for login."""
    username: str
    password: str


class RefreshToken(SQLModel):
    """Model for token refresh."""
    refresh_token: str