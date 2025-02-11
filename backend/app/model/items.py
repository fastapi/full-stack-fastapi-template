import uuid
from typing import Any

from sqlmodel import Field, Relationship, SQLModel, Session, select, func
from fastapi import HTTPException

from app.model.users import User



# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore

# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")

    @classmethod
    def create(cls, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> "Item":
        db_item = cls.model_validate(item_in, update={"owner_id": owner_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
    
    @classmethod
    def get_items(
        cls, session: Session, owner_id: uuid.UUID, is_superuser: bool, skip: int = 0, limit: int = 100
    ) -> Any:
        if is_superuser:
            count_statement = select(func.count()).select_from(cls)
            count = session.exec(count_statement).one()
            statement = select(cls).offset(skip).limit(limit)
            items = session.exec(statement).all()
        else:
            count_statement = (
                select(func.count())
                .select_from(cls)
                .where(cls.owner_id == owner_id)
            )
            count = session.exec(count_statement).one()
            statement = (
                select(cls)
                .where(cls.owner_id == owner_id)
                .offset(skip)
                .limit(limit)
            )
            items = session.exec(statement).all()
        return {"data": items, "count": count}

    @classmethod
    def get_by_id(cls, session: Session, item_id: uuid.UUID) -> "Item | None":
        return session.get(cls, item_id)

    @classmethod
    def update(cls, session: Session, item: "Item", item_in: ItemUpdate) -> "Item":
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def delete(cls, session: Session, item_id: uuid.UUID) -> None:
        item = session.get(cls, item_id)
        if item:
            session.delete(item)
            session.commit()


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
