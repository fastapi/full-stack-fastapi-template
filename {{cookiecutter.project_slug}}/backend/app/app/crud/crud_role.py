from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: RoleCreate, owner_id: int
    ) -> Role:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # def get_multi_by_owner(
    #     self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    # ) -> List[Role]:
    #     return (
    #         db.query(self.model)
    #         .filter(Role.owner_id == owner_id)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )


role = CRUDRole(Role)
