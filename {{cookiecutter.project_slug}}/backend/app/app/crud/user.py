import logging
from typing import List, Optional

from sqlalchemy.orm import Session

import app.models.user as models_user
import app.schemas.user as schemas_user
from app.core.security import get_password_hash, verify_password
from app.crud.base import CrudBase


class CrudUser(CrudBase):
    """
        CrudUser provides authentication methods like `authenticate`
        
        Basic methods like `get` are overridden to leverage auto-completion from IDE

        It also overrides `create` and `update` in order to hash the `password` appropriately
    """

    def get(self, db_session: Session, obj_id: int
    ) -> Optional[models_user.User]:
        return super(CrudUser, self).get(db_session, obj_id=obj_id)

    def get_multi(self, db_session: Session, *, skip=0, limit=100
    ) -> List[Optional[models_user.User]]:
        return super(CrudUser, self).get_multi(db_session, skip=skip, limit=limit)

    def get_by_email(self, db_session: Session, *, email: str
    ) -> Optional[models_user.User]:
        return (
            db_session.query(models_user.User)
            .filter(models_user.User.email == email)
            .first()
        )

    def authenticate(self, db_session: Session, *, email: str, password: str
    ) -> Optional[models_user.User]:
        user = self.get_by_email(db_session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        logging.info(
            f"\033[33mAuthenticated\033[0m \033[35mUser\033[0m\033[33m with\033[0m email={email}"
        )
        return user

    def create(self, db_session: Session, *, obj_in: schemas_user.UserCreate
    ) -> models_user.User:
        user = models_user.User(
            full_name=obj_in.full_name,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        logging.info(
            f"\033[33mCreating\033[0m \033[35mUser\033[0m\033[33m with\033[0m {obj_in}"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def update(
        self,
        db_session: Session,
        *,
        obj: models_user.User,
        obj_in: schemas_user.UserUpdate,
    ) -> models_user.User:
        user_data = obj.to_schema(schemas_user.UserUpdate).dict()
        update_data = obj_in.dict(skip_defaults=True)
        logging.info(
            f"\033[33mUpdating\033[0m \033[35mUser\033[0m {user_data} with {update_data}"
        )
        for field in user_data:
            if field in update_data:
                setattr(user, field, update_data[field])
        if obj_in.password:
            passwordhash = get_password_hash(obj_in.password)
            obj.hashed_password = passwordhash
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        logging.debug(f"User updated to {obj.to_schema(schemas_user.UserBaseInDB)}")
        return obj


user = CrudUser(models_user.User, schemas_user.UserBaseInDB)
