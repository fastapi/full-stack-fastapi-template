from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class RefreshTokenBase(BaseModel):
    token: str
    is_valid: bool = True


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenUpdate(RefreshTokenBase):
    is_valid: bool = Field(..., description="Deliberately disable a refresh token.")


class RefreshToken(RefreshTokenUpdate):
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
    refresh: Optional[bool] = False
    totp: Optional[bool] = False


class MagicTokenPayload(BaseModel):
    sub: Optional[UUID] = None
    fingerprint: Optional[UUID] = None


class WebToken(BaseModel):
    claim: str
