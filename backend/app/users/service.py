from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.users.constants import UserType
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    extra_data: dict[str, Any] = {
        "hashed_password": get_password_hash(user_create.password)
    }
    # Keep the legacy is_superuser flag and user_type consistent
    if user_create.user_type == UserType.ADMIN:
        extra_data["is_superuser"] = True
    elif user_create.is_superuser:
        extra_data["user_type"] = UserType.ADMIN
    db_obj = User.model_validate(user_create, update=extra_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    # Keep the legacy is_superuser flag and user_type consistent
    if "user_type" in user_data:
        extra_data["is_superuser"] = user_data["user_type"] == UserType.ADMIN
    elif user_data.get("is_superuser"):
        extra_data["user_type"] = UserType.ADMIN
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user
