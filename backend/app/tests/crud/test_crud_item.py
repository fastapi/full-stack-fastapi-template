import uuid
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app import crud
from app.models import Item, ItemCreate, ItemUpdate, User, UserCreate
from app.tests.utils.utils import random_lower_string, random_email

def test_create_item(db: Session) -> None:
    title = random_lower_string()
    description = random_lower_string()
    owner = create_random_user(db)
    item_in = ItemCreate(title=title, description=description)
    item = crud.create_item(session=db, item_in=item_in, owner_id=owner.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == owner.id

def test_get_item(db: Session) -> None:
    title = random_lower_string()
    description = random_lower_string()
    owner = create_random_user(db)
    item_in = ItemCreate(title=title, description=description)
    item = crud.create_item(session=db, item_in=item_in, owner_id=owner.id)
    stored_item = crud.get_item(session=db, item_id=item.id)
    assert stored_item
    assert item.id == stored_item.id
    assert item.title == stored_item.title
    assert item.description == stored_item.description
    assert item.owner_id == stored_item.owner_id

def test_update_item(db: Session) -> None:
    title = random_lower_string()
    description = random_lower_string()
    owner = create_random_user(db)
    item_in = ItemCreate(title=title, description=description)
    item = crud.create_item(session=db, item_in=item_in, owner_id=owner.id)
    new_title = random_lower_string()
    item_update = ItemUpdate(title=new_title)
    updated_item = crud.update_item(session=db, db_item=item, item_in=item_update)
    assert updated_item.title == new_title
    assert updated_item.description == description
    assert updated_item.id == item.id
    assert updated_item.owner_id == owner.id

def test_delete_item(db: Session) -> None:
    title = random_lower_string()
    description = random_lower_string()
    owner = create_random_user(db)
    item_in = ItemCreate(title=title, description=description)
    item = crud.create_item(session=db, item_in=item_in, owner_id=owner.id)
    deleted_item = crud.delete_item(session=db, item_id=item.id)
    assert deleted_item
    stored_item = crud.get_item(session=db, item_id=item.id)
    assert stored_item is None

def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    return crud.create_user(session=db, user_create=user_in)

def test_get_items(db: Session) -> None:
    owner = create_random_user(db)
    item1 = crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    item2 = crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    items = crud.get_items(session=db)
    assert len(items) >= 2
    assert item1 in items
    assert item2 in items

def test_get_items_by_owner(db: Session) -> None:
    owner1 = create_random_user(db)
    owner2 = create_random_user(db)
    item1 = crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner1.id)
    item2 = crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner2.id)
    items = crud.get_items_by_owner(session=db, owner_id=owner1.id)
    assert len(items) == 1
    assert item1 in items
    assert item2 not in items

def test_get_item_count(db: Session) -> None:
    initial_count = crud.get_item_count(session=db)
    owner = create_random_user(db)
    crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    final_count = crud.get_item_count(session=db)
    assert final_count == initial_count + 2

def test_get_item_count_by_owner(db: Session) -> None:
    owner = create_random_user(db)
    crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    crud.create_item(session=db, item_in=ItemCreate(title=random_lower_string()), owner_id=owner.id)
    count = crud.get_item_count_by_owner(session=db, owner_id=owner.id)
    assert count == 2
