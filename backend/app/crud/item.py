import uuid
from typing import List, Optional, Tuple

from sqlmodel import Session, select, func

from app.models.item import Item, ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """
    Create a new item.
    """
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item(*, session: Session, item_id: uuid.UUID) -> Optional[Item]:
    """
    Get an item by ID.
    """
    return session.get(Item, item_id)


def get_items(
    *, session: Session, owner_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100
) -> Tuple[List[Item], int]:
    """
    Get multiple items with pagination.
    """
    if owner_id:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
    else:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
    
    items = session.exec(statement).all()
    return items, count


def update_item(
    *, session: Session, db_item: Item, item_in: ItemUpdate
) -> Item:
    """
    Update an item.
    """
    update_dict = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_dict)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, item_id: uuid.UUID) -> None:
    """
    Delete an item.
    """
    item = session.get(Item, item_id)
    if item:
        session.delete(item)
        session.commit()