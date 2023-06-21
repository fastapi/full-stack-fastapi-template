from typing import Any, List, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from app.crud.base import CRUDBase
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: Union[int, Column[Any]]
    ) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Item(**obj_in_data, owner_id=owner_id)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: Union[int, Column[Any]],
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        result = await db.execute(
            select(self.model)
            .filter(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


item = CRUDItem(Item)
