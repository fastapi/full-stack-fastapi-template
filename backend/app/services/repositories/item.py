import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.db.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.repository import BaseRepository


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    """Repository for Item model operations."""
    
    def __init__(self):
        super().__init__(Item)
    
    def get_multi_by_owner(
        self, session: Session, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        """Get multiple items by owner ID with pagination."""
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()
    
    def create_with_owner(
        self, session: Session, *, obj_in: ItemCreate, owner_id: uuid.UUID
    ) -> Item:
        """Create a new item with owner ID."""
        obj_data = obj_in.model_dump()
        db_obj = Item(**obj_data, owner_id=owner_id)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj 