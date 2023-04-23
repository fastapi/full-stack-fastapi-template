import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):

    def create_strict(
            self, db: Session, *, obj_in: PermissionCreate, owner_id: int
    ) -> Permission:
        raise Exception(obj_in)
    def create_with_owner(
        self, db: Session, *, obj_in: PermissionCreate, owner_id: int
    ) -> Permission:
        obj_in_data = jsonable_encoder(obj_in)
        role_id = obj_in_data['role_id']['id']
        role = db.query(Role).get(role_id)
        obj_in_data['role'] = role
        del obj_in_data['role_id']
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_owner(
            self, db: Session, *, obj_in: PermissionUpdate, owner_id: int
    ) -> Permission:
        obj_in_data = db.query(Permission).get(obj_in.id)
        role = db.query(Role).get(obj_in.role_id['id'])
        permissions = self.format_permissions(obj_in.permissions)
        obj_in_data.object = obj_in.object
        obj_in_data.role = role
        obj_in_data.permissions = permissions
        db.commit()
        db.refresh(obj_in_data)
        return obj_in_data

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
    def format_permissions(self, permissions):
        formatted = {}
        for k, v in permissions.items():
            formatted[k] = 1 if v == "True" else 0
        return formatted

permission = CRUDPermission(Permission)
