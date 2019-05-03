from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SubItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    item_id = Column(Integer, ForeignKey("item.id"))
    item = relationship("Item", back_populates="sub_items")
