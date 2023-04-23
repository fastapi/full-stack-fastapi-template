from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Permission(Base):
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("Role", backref='permissions')
    object = Column(String, nullable=True)
    permissions = Column(JSON, nullable=True)
