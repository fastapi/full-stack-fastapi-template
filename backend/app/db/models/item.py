import uuid

from sqlmodel import Field, Relationship, SQLModel

from app.db.models.user import User


class Item(SQLModel, table=True):
    """
    Item model for database storage.
    
    This model represents an item in the system and is stored in PostgreSQL.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items") 