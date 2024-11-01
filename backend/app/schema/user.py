# Create and Read Schemas

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.constants import Gender


class UserPublicCreate(BaseModel):
    full_name: str
    phone_number: str | None = None
    email: EmailStr | None = None
    date_of_birth: datetime | None = None
    gender: Gender | None = None
    profile_picture: str | None = None
    preferences: str | None = None


class UserPublicUpdate(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    date_of_birth: datetime | None
    gender: Gender | None = None
    profile_picture: str | None = None
    preferences: str | None = None


class UserPublicRead(BaseModel):
    id: uuid.UUID
    phone_number: str
    full_name: str | None = None
    email: EmailStr | None = None
    date_of_birth: datetime | None = None
    gender: Gender | None = None
    profile_picture: str | None = None
    preferences: str | None = None

    class Config:
        from_attributes = True
        extra = "forbid"


class UserBusinessCreate(BaseModel):
    full_name: str | None = None
    email: EmailStr
    phone_number: str | None = None


class UserBusinessUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None


class UserBusinessRead(BaseModel):
    id: uuid.UUID
    full_name: str | None = None
    email: EmailStr
    phone_number: str | None = None

    class Config:
        from_attributes = True
        extra = "forbid"
