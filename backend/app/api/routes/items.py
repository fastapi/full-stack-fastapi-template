import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.api.deps import CurrentUser, SessionDep  # Custom dependencies for user and session
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message  # Importing models

router = APIRouter()  # Create an APIRouter instance for routing


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items for the logged-in user. If the user is a superuser, they can see all items.
    Otherwise, they can only see their own items.
    """
    # Check if the current user is a superuser
    if current_user.is_superuser:
        # Count all items in the database
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        # Retrieve items with pagination
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        # For non-superusers, only retrieve items owned by the logged-in user
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

    return ItemsPublic(data=items, count=count)  # Return items and total count


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get a single item by ID. Users can only access their own items unless they are a superuser.
    """
    item = session.get(Item, id)  # Retrieve item by ID
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")  # Item not found
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")  # Permission check
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create a new item. The item will be associated with the logged-in user.
    """
    # Create a new Item object, validating and assigning the owner (current user)
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)  # Add the new item to the session
    session.commit()  # Commit the transaction to the database
    session.refresh(item)  # Refresh the item object to get the updated values
    return item  # Return the newly created item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an existing item. Users can only update their own items unless they are superusers.
    """
    item = session.get(Item, id)  # Retrieve item by ID
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")  # Item not found
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")  # Permission check
    update_dict = item_in.model_dump(exclude_unset=True)  # Prepare update data
    item.sqlmodel_update(update_dict)  # Apply updates to the item
    session.add(item)  # Add updated item to session
    session.commit()  # Commit the transaction
    session.refresh(item)  # Refresh the item object to get the updated values
    return item  # Return the updated item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item. Users can only delete their own items unless they are superusers.
    """
    item = session.get(Item, id)  # Retrieve item by ID
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")  # Item not found
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")  # Permission check
    session.delete(item)  # Delete the item from the session
    session.commit()  # Commit the transaction
    return Message(message="Item deleted successfully")  # Return a success message
