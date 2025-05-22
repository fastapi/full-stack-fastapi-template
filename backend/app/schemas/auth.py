from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class TokenType(str, Enum):
    BEARER = "bearer"


class TokenBase(BaseModel):
    access_token: str
    token_type: str = TokenType.BEARER
    refresh_token: str


class Token(TokenBase):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserRegister(BaseModel):
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


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: str
    updated_at: Optional[str]
    last_login: Optional[str]

    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class OAuthTokenRequest(BaseModel):
    code: str
    redirect_uri: str


class SSOProvider(str, Enum):
    SAML = "saml"
    OIDC = "oidc"


class SSORequest(BaseModel):
    metadata_url: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uris: Optional[list[str]] = None
