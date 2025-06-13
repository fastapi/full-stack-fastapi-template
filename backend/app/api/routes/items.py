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
    limit: int = 100
) -> Any:
    """
    Retrieve items.
    
    This endpoint retrieves a list of items. For regular users, it returns only their own items.
    For superusers, it returns all items in the system.
    
    Parameters:
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    
    Returns a list of items and the total count.
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
def read_item(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
) -> Any:
    """
    Get item by ID.
    
    This endpoint retrieves a specific item by its ID.
    
    Parameters:
    - **id**: The UUID of the item to retrieve
    
    Returns the item details.
    
    Raises:
    - 404: If the item is not found
    - 400: If the user doesn't have permission to access this item
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ItemCreate
) -> Any:
    """
    Create new item.
    
    This endpoint allows users to create a new item.
    
    Parameters:
    - **title**: Required. The title of the item
    - **description**: Optional. A description of the item
    
    Returns the created item with its ID and owner information.
    
    Example request body:
    ```json
    {
        "title": "My Item",
        "description": "This is a description of my item"
    }
    ```
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
    
    This endpoint allows users to update an existing item.
    
    Parameters:
    - **id**: The UUID of the item to update
    - **title**: Optional. The updated title
    - **description**: Optional. The updated description
    
    Returns the updated item.
    
    Raises:
    - 404: If the item is not found
    - 400: If the user doesn't have permission to update this item
    
    Example request body:
    ```json
    {
        "title": "Updated Title",
        "description": "Updated description"
    }
    ```
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
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
) -> Message:
    """
    Delete an item.
    
    This endpoint allows users to delete an item.
    
    Parameters:
    - **id**: The UUID of the item to delete
    
    Returns a success message upon successful deletion.
    
    Raises:
    - 404: If the item is not found
    - 400: If the user doesn't have permission to delete this item
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
