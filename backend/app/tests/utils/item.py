from sqlmodel import Session

from app.models import Item, ItemCreate
from app.repositories.items import ItemRepository
from app.services.items import ItemService
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def item_service(session: Session) -> ItemService:
    return ItemService(repository=ItemRepository(session=session))


def create_random_item(session: Session) -> Item:
    user = create_random_user(session)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return item_service(session).create(item_create=item_in, owner_id=owner_id)
