import uuid

from sqlmodel import Session, col, func, select

from app.models import User


def get_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def get_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def list_users(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = list(session.exec(statement).all())
    return users, count


def create(*, session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def save(*, session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete(*, session: Session, user: User) -> None:
    session.delete(user)
    session.commit()
