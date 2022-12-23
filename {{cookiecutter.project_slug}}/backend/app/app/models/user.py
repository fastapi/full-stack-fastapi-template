from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class User(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean(), default=True)
    is_superuser: bool = Column(Boolean(), default=False)
    items: List["Item"] = relationship("Item", back_populates="owner")
