import uuid
from sqlmodel import Session

from app.model.items import Item, ItemCreate


class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def create_item(self, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        return Item.create(self.session, item_in, owner_id)
