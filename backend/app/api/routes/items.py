"""Item management API endpoints."""

import uuid

# Removed unused Any import
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> ItemsPublic:
    """Retrieve items."""
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    return ItemsPublic(data=items, count=count)


@router.get("/{item_id}")
def read_item(
    session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID,
) -> ItemPublic:
    """Get item by ID."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return ItemPublic.model_validate(item)


@router.post("/")
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ItemCreate,
) -> ItemPublic:
    """Create new item."""
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return ItemPublic.model_validate(item)


@router.put("/{item_id}")
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: uuid.UUID,
    item_in: ItemUpdate,
) -> ItemPublic:
    """Update an item."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return ItemPublic.model_validate(item)


@router.delete("/{item_id}")
def delete_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: uuid.UUID,
) -> Message:
    """Delete an item."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
