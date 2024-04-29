from typing import Any, List

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
)

from app.models import ItemPublic, ItemPublic, ItemsPublic, Store, StoreCreate, StoreInventoriesPublic, StoreInventoryUpdate, StoresPublic, StoreInventory, Message, Item

router = APIRouter()


@router.get("/", response_model=StoresPublic)
def read_store(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Store)
        count = session.exec(count_statement).one()
        statement = select(Store).offset(skip).limit(limit)
        stores = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Store)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Store)
            .offset(skip)
            .limit(limit)
        )
        stores = session.exec(statement).all()
    if len(stores) == 0:
        return StoresPublic(data=[], count=0)
    return StoresPublic(data=stores, count=count)


@router.get("/{id}/inventory", response_model=StoreInventoriesPublic)
def read_inventory(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get item by ID.
    """
    store_with_inventory = (
        session.query(StoreInventory.item_id,
            StoreInventory.store_id,
            StoreInventory.stock_unit, Item.title, Item.description, Item.revenue,Item.cost,
            Item.owner_id,
            StoreInventory.item_id
        )
        .join(Item,StoreInventory.item_id == Item.id)
        .where(StoreInventory.store_id == id)
        .all()
    )

    store_with_inventory_objects: List[ItemPublic] = []
    for item_tuple in store_with_inventory:
        item_public = ItemPublic(
            id=item_tuple[0],
            title=item_tuple[3],
            description=item_tuple[4],
            revenue=item_tuple[5],
            cost=item_tuple[6],
            units=item_tuple[2],
            owner_id=item_tuple[7]
        )
        store_with_inventory_objects.append(item_public)

    print(store_with_inventory_objects)

    if not store_with_inventory:
        raise HTTPException(status_code=404, detail="Store not found")

    if not current_user.is_superuser and (store_with_inventory.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return StoreInventoriesPublic(data=store_with_inventory_objects, count=0)


@router.post("/",response_model=Message)
def create_store(
    *, session: SessionDep, current_user: CurrentUser, store_in: StoreCreate
) -> Any:
    """
    Create new store.
    """
    store = Store.model_validate(store_in, update={"owner_id": current_user.id})
    session.add(store)
    session.commit()
    session.refresh(store)
    return Message(message="Item added successfully")


@router.post("/{id}/add", response_model=Message)
def create_store_inventory(
    *, session: SessionDep, current_user: CurrentUser, store_in: StoreInventoryUpdate
) -> Any:
    """
    Create new item.
    """
    storeInventory  = StoreInventory.model_validate(store_in, update={"owner_id": current_user.id})
    print(storeInventory)
    itemId = store_in.item_id
    item = session.get(Item, itemId)
    if item.units - store_in.stock_unit > 0:    
        statement = select(StoreInventory).where(
            StoreInventory.store_id == store_in.store_id,
            StoreInventory.item_id == store_in.item_id,
        )
        inventoryRecord = session.exec(statement).first()

        if inventoryRecord != None:
            print('inside')
            print(storeInventory)
            storeInventory =  session.get(StoreInventory, inventoryRecord.id)
            item.units = item.units + ( storeInventory.stock_unit -  store_in.stock_unit )
            storeInventory.stock_unit =   store_in.stock_unit
        else: 
            item.units = item.units - store_in.stock_unit
        session.add(item)
        session.add(storeInventory)
        session.commit()
        session.refresh(storeInventory)
        session.refresh(item)
        return Message(message="Item added successfully")
    raise HTTPException(status_code=400, detail="Not enough Items are available")