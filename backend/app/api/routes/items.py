import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, ItemServiceDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    item_service: ItemServiceDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items.
    """
    count: int
    items: list[Item]
    if current_user.is_superuser:
        count = item_service.repository.count()
        items = item_service.repository.get_all(skip=skip, limit=limit)
    else:
        count = item_service.repository.count_by_owner_id(owner_id=current_user.id)
        items = item_service.repository.get_all_by_owner_id(
            owner_id=current_user.id, skip=skip, limit=limit
        )

    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(
    item_service: ItemServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """
    Get item by id.
    """
    item = item_service.repository.get_by_id(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    item_service: ItemServiceDep,
    current_user: CurrentUser,
    item_in: ItemCreate,
) -> Any:
    """
    Create new item.
    """
    item = item_service.create(item_create=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    item_service: ItemServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = item_service.repository.get_by_id(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item = item_service.repository.update(item, update=update_dict)
    return item


@router.delete("/{id}")
def delete_item(
    item_service: ItemServiceDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Message:
    """
    Delete an item.
    """
    item = item_service.repository.get_by_id(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item_service.repository.delete(id)
    return Message(message="Item deleted successfully")
