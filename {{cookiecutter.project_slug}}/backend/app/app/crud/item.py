from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db_models.item import Item
from app.models.item import ItemCreate, ItemUpdate
from app.crud.base import CrudBase


class CrudItem(CrudBase):
    """
    This is provided as a showcase of which methods to override, with the benefit to adjusting
    both the types of the arguments and of the returned objects to the proper 'Item*' classes
    """

    def get(self, db_session: Session, id: int) -> Optional[Item]:
        return super(CrudItem, self).get(db_session, obj_id=id)

    def get_multi(self, db_session: Session, *, skip=0, limit=100) -> List[Optional[Item]]:
        return super(CrudItem, self).get_multi(db_session, skip=skip, limit=limit)

    def create(self, db_session: Session, *, item_in: ItemCreate, owner_id: int) -> Item:
        item_in_data = jsonable_encoder(item_in)
        item = Item(**item_in_data, owner_id=owner_id)
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    def update(self, db_session: Session, *, item: Item, item_in: ItemUpdate) -> Item:
        return super(CrudItem, self).update(db_session, obj=item, obj_in=item_in)


item = CrudItem(Item)
