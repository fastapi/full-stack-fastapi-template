import uuid
from typing import Any

from sqlmodel import Session
from fastapi import HTTPException

from app.model.items import Item, ItemCreate, ItemUpdate
from app.models import Message

class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def create_item(self, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        return Item.create(self.session, item_in, owner_id)

    def read_items(
        self, owner_id: uuid.UUID, is_superuser: bool, skip: int = 0, limit: int = 100
    ) -> Any:
        return Item.get_items(
            self.session,
            owner_id=owner_id,
            is_superuser=is_superuser,
            skip=skip,
            limit=limit
        )

    def read_item(self, item_id: uuid.UUID, owner_id: uuid.UUID, is_superuser: bool) -> Any:
        item = Item.get_by_id(self.session, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not is_superuser and (item.owner_id != owner_id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        return item

    def update_item(
        self, item_id: uuid.UUID, item_in: ItemUpdate, owner_id: uuid.UUID, is_superuser: bool
    ) -> Any:
        item = Item.get_by_id(self.session, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not is_superuser and (item.owner_id != owner_id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        return Item.update(self.session, item, item_in)

    def delete_item(self, item_id: uuid.UUID, owner_id: uuid.UUID, is_superuser: bool) -> Message:
        item = Item.get_by_id(self.session, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not is_superuser and (item.owner_id != owner_id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        Item.delete(self.session, item_id)
        return Message(message="Item deleted successfully")