import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, 
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100,
    category: str | None = None
) -> Any:
    """
    Retrieve items.
    """
    
    # Base query
    if current_user.is_superuser:
        query = select(Item)
        count_query = select(func.count()).select_from(Item)
    else:
        query = select(Item).where(Item.owner_id == current_user.id)
        count_query = select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
    
    # Apply category filter if provided
    if category:
        query = query.where(Item.category == category)
        count_query = count_query.where(Item.category == category)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute queries
    count = session.exec(count_query).one()
    items = session.exec(query).all()

    return ItemsPublic(data=items, count=count)


@router.get("/categories", response_model=list[str])
def get_item_categories(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get all unique item categories.
    """
    if current_user.is_superuser:
        statement = select(Item.category).distinct()
    else:
        statement = select(Item.category).where(
            Item.owner_id == current_user.id
        ).distinct()
    
    categories = session.exec(statement).all()
    # Filter out None values and return unique non-empty categories
    return [cat for cat in categories if cat]


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
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
