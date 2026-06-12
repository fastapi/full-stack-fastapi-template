from __future__ import annotations
from app.utils import get_datetime_utc
import uuid
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy import DateTime, String
from sqlmodel import Field, SQLModel

from app.users.constants import UserType

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    user_type: UserType = Field(
        default=UserType.NORMAL,
        sa_type=String(20),  # type: ignore[call-arg]
        index=True,
    )
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore[call-arg]
    )