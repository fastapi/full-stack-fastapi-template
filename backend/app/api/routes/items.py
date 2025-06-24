import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.openfga.fgaMiddleware import check_user_has_relation, create_fga_tuple, delete_fga_tuple, initialize_fga_client
from app.openfga.fgaMiddleware import check_user_has_permission
from openfga_sdk.client.models.tuple import ClientTuple

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100, get_completed: bool = False
) -> Any:
    """
    Retrieve items.
    """
    fga_client = initialize_fga_client()

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            # .where(Item.owner_id == current_user.id) # only returns items that the user owns
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            # .where(Item.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()
            
    if get_completed:
        item_ids = check_user_has_relation(fga_client, relation="completed", user=f"{current_user.email}")
        if len(item_ids) == 0:
            return ItemsPublic(data=[], count=0)
        else:
            # get those items with those ids
            items = [session.get(Item, id) for id in item_ids]

    return ItemsPublic(data=[ItemPublic.model_validate(item) for item in items], count=count)


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

    fga_client = initialize_fga_client()
    create_fga_tuple(fga_client, [
        ClientTuple(user=f"user:{current_user.email}", relation="owner", object=f"item:{item.id}")
    ])
    return item


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    
    """
    Update an item.
    """
    # check if the user has the permission to update the item
    # if not, raise an error
    # if the user has the permission, update the item
    # return the updated item

    fga_client = initialize_fga_client()
    if not check_user_has_permission(fga_client, ClientTuple(user=f"user:{current_user.id}", relation="update", object=f"item:{id}")):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
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

@router.get("/{id}/can-update", response_model=bool)
async def can_update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
):
    fga_client = initialize_fga_client()
    has_permission = check_user_has_permission(fga_client, ClientTuple(user=f"user:{current_user.id}", relation="update", object=f"item:{id}"))
    
    return has_permission

@router.delete("/{id}")
async def delete_item(
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

    fga_client = initialize_fga_client()
    delete_fga_tuple(fga_client, [ClientTuple(user=f"user:{current_user.id}", relation="owner", object=f"item:{id}")])
    
    return Message(message="Item deleted successfully")
