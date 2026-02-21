import uuid

from sqlmodel import Session

from app.models import Item, ItemCreate, ItemUpdate, User
from app.repositories import item_repository
from app.services.exceptions import ForbiddenError, NotFoundError


def list_items_for_user(
    *, session: Session, current_user: User, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    if current_user.is_superuser:
        return item_repository.list_all(session=session, skip=skip, limit=limit)
    return item_repository.list_by_owner(
        session=session, owner_id=current_user.id, skip=skip, limit=limit
    )


def get_item_for_user(*, session: Session, current_user: User, item_id: uuid.UUID) -> Item:
    item = item_repository.get_by_id(session=session, item_id=item_id)
    if item is None:
        raise NotFoundError("Item not found")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise ForbiddenError("Not enough permissions")
    return item


def create_item_for_owner(
    *, session: Session, item_in: ItemCreate, owner_id: uuid.UUID
) -> Item:
    item = Item.model_validate(item_in, update={"owner_id": owner_id})
    return item_repository.create(session=session, item=item)


def create_item_for_user(
    *, session: Session, current_user: User, item_in: ItemCreate
) -> Item:
    return create_item_for_owner(session=session, item_in=item_in, owner_id=current_user.id)


def update_item_for_user(
    *,
    session: Session,
    current_user: User,
    item_id: uuid.UUID,
    item_in: ItemUpdate,
) -> Item:
    item = get_item_for_user(session=session, current_user=current_user, item_id=item_id)
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    return item_repository.save(session=session, item=item)


def delete_item_for_user(
    *, session: Session, current_user: User, item_id: uuid.UUID
) -> None:
    item = get_item_for_user(session=session, current_user=current_user, item_id=item_id)
    item_repository.delete_one(session=session, item=item)
