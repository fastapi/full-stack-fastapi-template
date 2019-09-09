from app import crud
from app.schemas.sub_item import SubItemCreate, SubItemUpdate
from app.tests.utils.utils import random_lower_string
from app.tests.utils.item import create_random_item
from app.db.session import db_session


ITEM = create_random_item()
SUB_ITEM = None


def test_create_sub_item():
    global SUB_ITEM
    name = random_lower_string()
    sub_item_in = SubItemCreate(name=name, item_id=ITEM.id)
    SUB_ITEM = crud.sub_item.create(db_session=db_session, obj_in=sub_item_in)
    assert SUB_ITEM.name == name
    assert SUB_ITEM.item_id == ITEM.id


def test_get_sub_item():
    stored_sub_item = crud.sub_item.get(db_session=db_session, obj_id=SUB_ITEM.id)
    assert stored_sub_item.id == SUB_ITEM.id
    assert stored_sub_item.name == SUB_ITEM.name
    assert stored_sub_item.item_id == SUB_ITEM.item_id

    assert stored_sub_item.item is not None
    assert stored_sub_item.item.title == ITEM.title


def test_update_sub_item():
    new_name = random_lower_string()
    sub_item_update = SubItemUpdate(name=new_name)
    updated_sub_item = crud.sub_item.update(
        db_session=db_session, obj=SUB_ITEM, obj_in=sub_item_update
    )
    assert updated_sub_item.id == SUB_ITEM.id
    assert updated_sub_item.name == new_name


def test_delete_sub_item():
    assert crud.sub_item.delete(db_session=db_session, obj_id=SUB_ITEM.id) == 1
    assert crud.sub_item.get(db_session=db_session, obj_id=SUB_ITEM.id) is None
