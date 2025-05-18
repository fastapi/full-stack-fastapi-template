from sqlmodel import Session

from app.modules.items.domain.models import Item, ItemCreate
from app.modules.items.repository.item_repo import ItemRepository
from app.modules.items.services.item_service import ItemService
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item_repo = ItemRepository(db)
    item_service = ItemService(item_repo)
    return item_service.create_item(owner_id=owner_id, item_create=item_in)
