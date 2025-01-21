import uuid
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Meeting, MeetingCreate, MeetingUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
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
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_meeting(*, session: Session, meeting_in: MeetingCreate) -> Meeting:
    db_obj = Meeting.model_validate(meeting_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_meeting(*, session: Session, meeting_id: UUID) -> Meeting | None:
    return session.get(Meeting, meeting_id)


def get_meetings(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[Meeting], int]:
    statement = select(Meeting).offset(skip).limit(limit)
    meetings = session.exec(statement).all()
    total = session.query(Meeting).count()
    return meetings, total


def update_meeting(
    *, session: Session, db_obj: Meeting, obj_in: MeetingUpdate
) -> Meeting:
    update_data = obj_in.model_dump(exclude_unset=True)
    db_obj.sqlmodel_update(update_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_meeting(*, session: Session, meeting_id: UUID) -> Meeting | None:
    meeting = session.get(Meeting, meeting_id)
    if meeting:
        session.delete(meeting)
        session.commit()
    return meeting
