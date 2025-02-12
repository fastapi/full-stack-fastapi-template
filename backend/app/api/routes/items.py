import uuid
from typing import Any

from fastapi import APIRouter


from app.api.deps import CurrentUser, SessionDep
from backend.app.model.items_model import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from backend.app.model.user_model import Message
from app.service.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    item_service = ItemService(session)
    result = item_service.read_items(
        owner_id=current_user.id,
        is_superuser=current_user.is_superuser,
        skip=skip,
        limit=limit,
    )
    return ItemsPublic(data=result["data"], count=result["count"])


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item_service = ItemService(session)
    return item_service.read_item(
        item_id=id, owner_id=current_user.id, is_superuser=current_user.is_superuser
    )

@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item_service = ItemService(session)
    return item_service.create_item(item_in, current_user.id)


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
    item_service = ItemService(session)
    return item_service.update_item(
        item_id=id,
        item_in=item_in,
        owner_id=current_user.id,
        is_superuser=current_user.is_superuser,
    )


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item_service = ItemService(session)
    item_service.delete_item(
        item_id=id, owner_id=current_user.id, is_superuser=current_user.is_superuser
    )
