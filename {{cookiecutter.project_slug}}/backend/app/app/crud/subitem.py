from typing import Optional
from sqlalchemy.orm import Session, subqueryload

from app.models.subitem import SubItem
from app.crud.base import CrudBase


class CrudSubItem(CrudBase):
    """
    This example shows how to change the behaviour of a default GET operation (by returning the foreign objects with all its attribute, instead of solely its id)
    """

    def get(self, db_session: Session, obj_id: int) -> Optional[SubItem]:
        return (
            db_session.query(SubItem)
            .options(subqueryload(SubItem.item))
            .get(obj_id)
        )


subitem = CrudSubItem(SubItem)
