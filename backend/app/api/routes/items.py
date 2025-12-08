import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message, ItemActivitiesPublic, ItemActivityPublic
from app.crud import create_activity, update_item_score
from app.utils import increment_view_count, get_trending_items
from app.core.config import settings

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

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


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Track view activity
    if getattr(settings, 'ENABLE_ACTIVITY_TRACKING', True):
        create_activity(
            session=session,
            item_id=id,
            user_id=current_user.id,
            activity_type="view",
            activity_metadata="Item viewed"
        )
        increment_view_count(session=session, item_id=id)
    
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Track update activity and refresh activity scores
    if getattr(settings, 'ENABLE_ACTIVITY_TRACKING', True):
        create_activity(
            session=session,
            item_id=id,
            user_id=current_user.id,
            activity_type="update",
            activity_metadata=f"Item updated: {item_in.title or 'description changed'}"
        )
        # THIS TRIGGERS THE INFINITE LOOP when user has multiple items!
        update_item_score(session=session, item_id=id)
    
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Track deletion activity before deleting
    if getattr(settings, 'ENABLE_ACTIVITY_TRACKING', True):
        create_activity(
            session=session,
            item_id=id,
            user_id=current_user.id,
            activity_type="delete",
            activity_metadata="Item deleted"
        )
    
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")


@router.get("/trending/list", response_model=ItemsPublic)
def get_trending(
    session: SessionDep, current_user: CurrentUser, limit: int = 10
) -> Any:
    """
    Get trending items based on activity scores.
    """
    if current_user.is_superuser:
        items = get_trending_items(session=session, limit=limit)
    else:
        items = get_trending_items(session=session, limit=limit, owner_id=current_user.id)
    
    return ItemsPublic(data=items, count=len(items))


@router.get("/{id}/activity", response_model=ItemActivitiesPublic)
def get_item_activity(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID, limit: int = 50
) -> Any:
    """
    Get activity history for an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    from app.models import ItemActivity
    statement = (
        select(ItemActivity)
        .where(ItemActivity.item_id == id)
        .order_by(ItemActivity.timestamp.desc())
        .limit(limit)
    )
    activities = session.exec(statement).all()
    
    return ItemActivitiesPublic(data=activities, count=len(activities))
