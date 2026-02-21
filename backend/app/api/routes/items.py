import uuid
from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.services import item_service
from app.services.exceptions import ServiceError

router = APIRouter(prefix="/items", tags=["items"])


def _raise_http_from_service_error(exc: ServiceError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    items, count = item_service.list_items_for_user(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    try:
        return item_service.get_item_for_user(
            session=session, current_user=current_user, item_id=id
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    return item_service.create_item_for_user(
        session=session, current_user=current_user, item_in=item_in
    )


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
    try:
        return item_service.update_item_for_user(
            session=session, current_user=current_user, item_id=id, item_in=item_in
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    try:
        item_service.delete_item_for_user(
            session=session, current_user=current_user, item_id=id
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return Message(message="Item deleted successfully")
