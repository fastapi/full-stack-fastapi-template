import uuid
from typing import Any

from sqlmodel import Session

from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
from app.services import auth_service, item_service, user_service


def create_user(*, session: Session, user_create: UserCreate) -> User:
    return user_service.create_user(session=session, user_create=user_create)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    return user_service.update_user(session=session, db_user=db_user, user_in=user_in)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    return user_service.get_user_by_email(session=session, email=email)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    return auth_service.authenticate(session=session, email=email, password=password)


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    return item_service.create_item_for_owner(
        session=session, item_in=item_in, owner_id=owner_id
    )
