import uuid
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import ItemCreate, ItemUpdate


class Item:
    def __init__(self, session: Session):
        self.session = session

    def create(cls, item_in: ItemCreate, owner_id: uuid.UUID) -> "Item":
        db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
        cls.session.add(db_item)
        cls.session.commit()
        cls.session.refresh(db_item)
        return db_item

    def get_items(
        cls,
        owner_id: uuid.UUID,
        is_superuser: bool,
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        if is_superuser:
            count_statement = select(func.count()).select_from(Item)
            count = cls.session.exec(count_statement).one()
            statement = select(Item).offset(skip).limit(limit)
            items = cls.session.exec(statement).all()
        else:
            count_statement = (
                select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
            )
            count = cls.session.exec(count_statement).one()
            statement = (
                select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
            )
            items = cls.session.exec(statement).all()
        return {"data": items, "count": count}

    def get_by_id(cls, item_id: uuid.UUID) -> "Item | None":
        return cls.session.get(Item, item_id)

    def update(cls, item: "Item", item_in: ItemUpdate) -> "Item":
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        cls.session.add(item)
        cls.session.commit()
        cls.session.refresh(item)
        return item

    def delete(cls, item_id: uuid.UUID) -> None:
        item = cls.session.get(Item, item_id)
        if item:
            cls.session.delete(item)
            cls.session.commit()
