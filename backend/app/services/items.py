import uuid

from app.models import Item, ItemCreate
from app.repositories.items import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def create(self, *, item_create: ItemCreate, owner_id: uuid.UUID) -> Item:
        db_obj = Item.model_validate(item_create, update={"owner_id": owner_id})
        return self.repository.create(db_obj)
