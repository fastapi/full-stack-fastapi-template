from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models import item as models_item
from app.schemas import item as schemas_item
from app.crud.base import CrudBase


class CrudItem(CrudBase):
    """
    This is provided as a showcase of which methods to override, with the benefit to adjusting
    both the types of the arguments and of the returned objects to the proper 'Item*' classes
    """

    def get(self, db_session: Session, id: int
    ) -> Optional[models_item.Item]:
        return super(CrudItem, self).get(db_session, obj_id=id)

    def get_multi(self, db_session: Session, *, skip=0, limit=100
    ) -> List[Optional[models_item.Item]]:
        return super(CrudItem, self).get_multi(db_session, skip=skip, limit=limit)

    def get_multi_by_owner(db_session: Session, *, owner_id: int, skip=0, limit=100
    ) -> List[Optional[models_item.Item]]:
        return self.get_multi_by(db_session, owner_id=owner_id, skip=skip, limit=limit)

    def create(self, db_session: Session, *, item_in: schemas_item.ItemCreate
    ) -> models_item.Item:
        return super(CrudItem, self).create(db_session, obj_in=item_in)

    def update(self, db_session: Session, *, item: models_item.Item, item_in: schemas_item.ItemUpdate
    ) -> models_item.Item:
        return super(CrudItem, self).update(db_session, obj=item, obj_in=item_in)


item = CrudItem(models_item.Item, schemas_item.ItemInDBBase)
