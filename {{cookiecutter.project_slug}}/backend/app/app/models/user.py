from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Token  # noqa: F401


class User(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    full_name: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    totp_secret: Mapped[Optional[str]] = mapped_column(nullable=True)
    totp_counter: Mapped[Optional[str]] = mapped_column(nullable=True)
    email_validated: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    refresh_tokens: Mapped[list["Token"]] = relationship(back_populates="authenticates", lazy="dynamic")
