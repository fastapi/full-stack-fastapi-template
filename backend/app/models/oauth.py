"""OAuth state model for CSRF protection."""
from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import BaseDBModel


class OAuthStateBase(SQLModel):
    """Base OAuth state model."""
    state_token: str = Field(unique=True, index=True)
    provider: str = Field(max_length=50)
    redirect_uri: str = Field(max_length=500)
    expires_at: datetime
    used: bool = Field(default=False)


class OAuthState(OAuthStateBase, BaseDBModel, table=True):
    """OAuth state for CSRF protection stored in database."""
    __tablename__ = "oauth_state"


class OAuthStateCreate(OAuthStateBase):
    """Schema for creating OAuth state."""
    pass


class OAuthStateUpdate(SQLModel):
    """Schema for updating OAuth state."""
    used: bool = True


class OAuthStatePublic(OAuthStateBase):
    """Public schema for OAuth state."""
    id: UUID
    created_at: datetime
    updated_at: datetime