from sqlmodel import Session

from app.service.item_service import ItemService
from app.model.items import Item, ItemCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item_service = ItemService(db)
    item = item_service.create_item(item_in, owner_id)
    return item
