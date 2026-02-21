import uuid

from sqlmodel import Session, col, delete, func, select

from app.models import Item


def get_by_id(*, session: Session, item_id: uuid.UUID) -> Item | None:
    return session.get(Item, item_id)


def list_all(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Item], int]:
    count_statement = select(func.count()).select_from(Item)
    count = session.exec(count_statement).one()
    statement = (
        select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
    )
    items = list(session.exec(statement).all())
    return items, count


def list_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    count_statement = (
        select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Item)
        .where(Item.owner_id == owner_id)
        .order_by(col(Item.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(session.exec(statement).all())
    return items, count


def create(*, session: Session, item: Item) -> Item:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def save(*, session: Session, item: Item) -> Item:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_one(*, session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()


def delete_by_owner(*, session: Session, owner_id: uuid.UUID) -> None:
    statement = delete(Item).where(col(Item.owner_id) == owner_id)
    session.exec(statement)
