from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Token(Base):
    token = Column(String, primary_key=True, index=True)
    is_valid = Column(Boolean(), default=True)
    authenticates_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    authenticates = relationship("User", back_populates="refresh_tokens")
