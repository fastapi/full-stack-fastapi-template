import uuid
from typing import Any, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Session, select, func

from app.core.security import get_password_hash, verify_password


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)  # type: ignore

    @classmethod
    def create(cls, session: Session, user_create: UserCreate) -> "User":
        db_obj = cls.model_validate(
            user_create, update={"hashed_password": get_password_hash(user_create.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, session: Session, db_user: "User", user_in: UserUpdate) -> Any:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> "User | None":
        statement = select(cls).where(cls.email == email)
        return session.exec(statement).first()

    @classmethod
    def get_by_id(cls, session: Session, user_id: str) -> "User | None":
        statement = select(cls).where(cls.id == uuid.UUID(user_id))
        return session.exec(statement).first()

    @classmethod
    def get_users(cls, session: Session, skip: int = 0, limit: int = 100) -> dict:
        count_statement = select(func.count()).select_from(cls)
        count = session.exec(count_statement).one()
        statement = select(cls).offset(skip).limit(limit)
        users = session.exec(statement).all()
        return {"data": users, "count": count}

    @classmethod
    def delete_user(cls, session: Session, user_id: str) -> None:
        user = cls.get_by_id(session, user_id)
        if user:
            session.delete(user)
            session.commit()


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
