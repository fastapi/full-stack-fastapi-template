import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message, StandardResponse
from app.services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=StandardResponse[ItemsPublic])
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        count = item_service.count_items(session=session)
        items = item_service.get_items(session=session, skip=skip, limit=limit)
    else:
        count = item_service.count_items_by_owner(session=session, owner_id=current_user.id)
        items = item_service.get_items_by_owner(
            session=session, owner_id=current_user.id, skip=skip, limit=limit
        )

    return StandardResponse(
        data=ItemsPublic(data=items, count=count),
        message="Items retrieved successfully"
    )


@router.get("/{id}", response_model=StandardResponse[ItemPublic])
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = item_service.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return StandardResponse(
        data=item,
        message="Item retrieved successfully"
    )


@router.post("/", response_model=StandardResponse[ItemPublic])
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = item_service.create_item(
        session=session, item_create=item_in, owner_id=current_user.id
    )
    
    return StandardResponse(
        data=item,
        message="Item created successfully"
    )


@router.put("/{id}", response_model=StandardResponse[ItemPublic])
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
    item = item_service.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_item = item_service.update_item(
        session=session, db_item=item, item_update=item_in
    )
    
    return StandardResponse(
        data=updated_item,
        message="Item updated successfully"
    )


@router.delete("/{id}", response_model=StandardResponse[Message])
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Delete an item.
    """
    item = item_service.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    item_service.delete_item(session=session, item_id=id)
    
    return StandardResponse(
        data=Message(message="Item deleted successfully"),
        message="Item deleted successfully"
    ) 