from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Role(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

    pms = relationship("Permission", backref="roles")
