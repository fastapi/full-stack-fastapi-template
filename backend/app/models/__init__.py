# Import all models here so they're properly registered with SQLAlchemy
from app.models.base import BaseDBModel, TimestampMixin
from app.models.user import (
    UserRole,
    OAuthProvider,
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserPublic,
    UserLogin,
    TokenPayload,
    TokenPair,
    RefreshTokenBase,
    RefreshToken,
    RefreshTokenCreate,
    RefreshTokenPublic,
    PasswordResetRequest,
    PasswordResetConfirm,
)

# This ensures that SQLModel knows about all models for migrations
__all__ = [
    'BaseDBModel',
    'TimestampMixin',
    'UserRole',
    'OAuthProvider',
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserInDB',
    'UserPublic',
    'UserLogin',
    'TokenPayload',
    'TokenPair',
    'RefreshTokenBase',
    'RefreshToken',
    'RefreshTokenCreate',
    'RefreshTokenPublic',
    'PasswordResetRequest',
    'PasswordResetConfirm',
]
