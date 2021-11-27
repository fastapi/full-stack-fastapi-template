import pytest
#from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.item import ItemCreate, ItemUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


async def test_create_item(async_get_db: AsyncSession) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = await create_random_user(async_get_db)
    item = await crud.item.create_with_owner(db=async_get_db, obj_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == user.id


async def test_get_item(async_get_db: AsyncSession) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = await create_random_user(async_get_db)
    item = await crud.item.create_with_owner(db=async_get_db, obj_in=item_in, owner_id=user.id)
    stored_item = await crud.item.get(db=async_get_db, id=item.id)
    assert stored_item
    assert item.id == stored_item.id
    assert item.title == stored_item.title
    assert item.description == stored_item.description
    assert item.owner_id == stored_item.owner_id


async def test_update_item(async_get_db: AsyncSession) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = await create_random_user(async_get_db)
    item = await crud.item.create_with_owner(db=async_get_db, obj_in=item_in, owner_id=user.id)
    description2 = random_lower_string()
    item_update = ItemUpdate(description=description2)
    item2 = await crud.item.update(db=async_get_db, db_obj=item, obj_in=item_update)
    assert item.id == item2.id
    assert item.title == item2.title
    assert item2.description == description2
    assert item.owner_id == item2.owner_id


async def test_delete_item(async_get_db: AsyncSession) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = await create_random_user(async_get_db)
    item = await crud.item.create_with_owner(db=async_get_db, obj_in=item_in, owner_id=user.id)
    item2 = await crud.item.remove(db=async_get_db, id=item.id)
    item3 = await crud.item.get(db=async_get_db, id=item.id)
    assert item3 is None
    assert item2.id == item.id
    assert item2.title == title
    assert item2.description == description
    assert item2.owner_id == user.id
