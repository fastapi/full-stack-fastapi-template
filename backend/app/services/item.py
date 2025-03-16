import uuid
from typing import List, Optional

from sqlmodel import Session, func, select

from app.db.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.repositories.item import ItemRepository


# Create a singleton instance of the repository
item_repository = ItemRepository()


def get_item(session: Session, item_id: uuid.UUID) -> Optional[Item]:
    """Get an item by ID."""
    return item_repository.get(session=session, id=item_id)


def get_items(session: Session, skip: int = 0, limit: int = 100) -> List[Item]:
    """Get multiple items with pagination."""
    return item_repository.get_multi(session=session, skip=skip, limit=limit)


def get_items_by_owner(
    session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[Item]:
    """Get multiple items by owner ID with pagination."""
    return item_repository.get_multi_by_owner(
        session=session, owner_id=owner_id, skip=skip, limit=limit
    )


def create_item(session: Session, item_create: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item with owner ID."""
    return item_repository.create_with_owner(
        session=session, obj_in=item_create, owner_id=owner_id
    )


def update_item(session: Session, db_item: Item, item_update: ItemUpdate) -> Item:
    """Update an item."""
    return item_repository.update(session=session, db_obj=db_item, obj_in=item_update)


def delete_item(session: Session, item_id: uuid.UUID) -> Optional[Item]:
    """Delete an item by ID."""
    return item_repository.remove(session=session, id=item_id)


def count_items(session: Session) -> int:
    """Count all items."""
    return session.exec(select(func.count()).select_from(Item)).one()


def count_items_by_owner(session: Session, owner_id: uuid.UUID) -> int:
    """Count items by owner ID."""
    return session.exec(
        select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
    ).one() 