import uuid
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import User, UserCreate, UserUpdate


class UserModel:
    def __init__(self, session: Session):
        self.session = session

    def create(cls, user_create: UserCreate) -> "User":
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        cls.session.add(db_obj)
        cls.session.commit()
        cls.session.refresh(db_obj)
        return db_obj

    def update(cls, db_user: "User", user_in: UserUpdate) -> Any:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        cls.session.add(db_user)
        cls.session.commit()
        cls.session.refresh(db_user)
        return db_user

    def get_by_email(cls, email: str) -> "User | None":
        statement = select(User).where(User.email == email)
        return cls.session.exec(statement).first()

    def get_by_id(cls, user_id: str) -> "User | None":
        statement = select(User).where(User.id == uuid.UUID(user_id))
        return cls.session.exec(statement).first()

    def get_users(cls, skip: int = 0, limit: int = 100) -> dict:
        count_statement = select(func.count()).select_from(User)
        count = cls.session.exec(count_statement).one()
        statement = select(User).offset(skip).limit(limit)
        users = cls.session.exec(statement).all()
        return {"data": users, "count": count}

    def delete_user(cls, user_id: str) -> None:
        user = cls.get_by_id(user_id)
        if user:
            cls.session.delete(user)
            cls.session.commit()
