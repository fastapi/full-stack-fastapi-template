from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr, Field, validator
from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, func
from sqlmodel import Field as SQLModelField, Relationship, SQLModel

from app.models.base import BaseDBModel, TimestampMixin


class UserRole(str, Enum):
    """User roles for role-based access control."""
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"


class UserBase(SQLModel):
    """Base user model with common fields."""
    email: EmailStr = SQLModelField(
        ...,
        sa_column=Column(String(255), unique=True, nullable=False, index=True),
    )
    is_active: bool = Field(default=True, nullable=False)  # Changed from False to True so all new users are active by default
    is_verified: bool = Field(default=False, nullable=False)
    email_verified: bool = Field(default=False, nullable=False)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: UserRole = Field(
        default=UserRole.USER,
        nullable=False,
        sa_column=Column(SQLEnum(UserRole), server_default=UserRole.USER.value, nullable=False),
    )
    last_login: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    
    # OAuth fields
    sso_provider: Optional[OAuthProvider] = Field(
        default=None,
        sa_column=Column(SQLEnum(OAuthProvider)),
    )
    sso_id: Optional[str] = Field(
        default=None,
        max_length=255,
        index=True,
        sa_column=Column(String(255), index=True),
    )
    
    # Password hash (nullable for OAuth users)
    hashed_password: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
                "role": "user",
            }
        }


class UserCreate(SQLModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(SQLModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "full_name": "New Name",
                "is_active": True,
                "is_verified": True,
                "role": "user",
            }
        }


class UserInDB(UserBase, BaseDBModel, table=True):
    """User model for database representation."""
    __tablename__ = "users"
    
    # Relationships
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    
    # Override the base fields to make them compatible with SQLModel
    id: UUID = SQLModelField(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    created_at: datetime = SQLModelField(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = SQLModelField(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class UserPublic(UserBase):
    """Public user schema (excludes sensitive data)."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
                "email_verified": True,
                "role": "user",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        }


class UserLogin(SQLModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class TokenPayload(SQLModel):
    """Payload for JWT tokens."""
    sub: UUID
    exp: int
    iat: int
    type: str
    jti: Optional[str] = None
    scopes: List[str] = []
    
    class Config:
        orm_mode = True
        json_encoders = {
            UUID: str,
        }


class TokenPair(SQLModel):
    """Schema for access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenBase(SQLModel):
    """Base schema for refresh tokens."""
    token: str = SQLModelField(..., index=True)
    expires_at: datetime
    is_revoked: bool = Field(default=False, nullable=False)
    user_agent: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)


class RefreshToken(RefreshTokenBase, BaseDBModel, table=True):
    """Refresh token model for database storage."""
    __tablename__ = "refresh_tokens"
    
    user_id: UUID = SQLModelField(
        foreign_key="users.id",
        index=True,
    )
    user: UserInDB = Relationship(back_populates="refresh_tokens")
    
    # Override the base fields to make them compatible with SQLModel
    id: UUID = SQLModelField(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    created_at: datetime = SQLModelField(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = SQLModelField(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class RefreshTokenCreate(RefreshTokenBase):
    """Schema for creating a new refresh token."""
    user_id: UUID


class RefreshTokenPublic(RefreshTokenBase):
    """Public schema for refresh tokens."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: str,
        }


class PasswordResetRequest(SQLModel):
    """Schema for requesting a password reset."""
    email: EmailStr


class PasswordResetConfirm(SQLModel):
    """Schema for confirming a password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class NewPassword(SQLModel):
    """Schema for setting a new password."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UpdatePassword(SQLModel):
    """Schema for updating a user's password."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserRegister(UserCreate):
    """Schema for user registration."""
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }


class UsersPublic(SQLModel):
    """Schema for returning a paginated list of users."""
    count: int = Field(..., description="Total number of users")
    data: List[UserPublic] = Field(..., description="List of users")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }


class UserUpdateMe(SQLModel):
    """Schema for updating the current user's profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "full_name": "New Name"
            }
        }
