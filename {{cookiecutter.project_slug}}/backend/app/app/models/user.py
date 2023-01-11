from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, String, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Token  # noqa: F401


class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    created = Column(DateTime, server_default=func.now(), nullable=False)
    modified = Column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    totp_secret = Column(String, nullable=True)
    totp_counter = Column(Integer, nullable=True)
    email_validated = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    refresh_tokens = relationship("Token", back_populates="authenticates", lazy="dynamic")
