import uuid
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    user_data = user_create.model_dump()
    user_data.pop("password", None)  # Remove password from user data
    hashed_password = get_password_hash(user_create.password)
    
    db_obj = User(
        **user_data,
        hashed_password=hashed_password
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in user_data:
        password = user_data.pop("password")
        hashed_password = get_password_hash(password)
        user_data["hashed_password"] = hashed_password
    
    for field, value in user_data.items():
        setattr(db_user, field, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    item_data = item_in.model_dump()
    db_item = Item(
        **item_data,
        owner_id=owner_id
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
