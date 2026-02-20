from sqlmodel import Session

from app.items import service as item_service
from app.items.models import Item
from app.items.schemas import ItemCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return item_service.create_item(session=db, item_in=item_in, owner_id=owner_id)
