import uuid
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import Item, ItemCreate, ItemUpdate


class ItemModel:
    def __init__(self, session: Session):
        self.session = session

    def create(self, item_create: ItemCreate, owner_id: uuid.UUID) -> Item:
        db_obj = Item.model_validate(
            item_create,
            update={"owner_id": owner_id},
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, db_item: Item, item_in: ItemUpdate) -> Item:
        item_data = item_in.model_dump(exclude_unset=True)
        db_item.sqlmodel_update(item_data)
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def get_by_id(self, item_id: str) -> "Item | None":
        statement = select(Item).where(Item.id == uuid.UUID(item_id))
        return self.session.exec(statement).first()

    def get_items(self, skip: int = 0, limit: int = 100, owner_id: uuid.UUID | None = None) -> dict:
        query = select(Item)
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
            
        count_statement = select(func.count()).select_from(query.subquery())
        count = self.session.exec(count_statement).one()
        
        query = query.offset(skip).limit(limit)
        items = self.session.exec(query).all()
        return {"data": items, "count": count}

    def delete_item(self, item_id: str) -> None:
        item = self.get_by_id(item_id)
        if item:
            self.session.delete(item)
            self.session.commit()
