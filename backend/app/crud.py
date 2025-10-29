import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.core.security import get_password_hash, verify_password
from app.models import Ingestion, User, UserCreate, UserUpdate


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


def get_ingestions(
    *,
    session: Session,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Ingestion], int]:
    """
    Get user's ingestions with pagination.

    Returns tuple of (ingestions, total_count).
    """
    # Count total ingestions for this user
    count_statement = (
        select(func.count()).select_from(Ingestion).where(Ingestion.owner_id == owner_id)
    )
    count = session.exec(count_statement).one()

    # Get paginated ingestions
    statement = (
        select(Ingestion)
        .where(Ingestion.owner_id == owner_id)
        .order_by(Ingestion.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    ingestions = session.exec(statement).all()

    return list(ingestions), count
