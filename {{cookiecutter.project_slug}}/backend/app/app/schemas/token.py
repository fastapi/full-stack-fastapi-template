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
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
    refresh: Optional[bool] = False
