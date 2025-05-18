"""
Item repository.

This module provides database access functions for item operations.
"""
import uuid
from typing import List, Optional, Tuple

from sqlmodel import Session, col, select

from app.core.db import BaseRepository
from app.modules.items.domain.models import Item


class ItemRepository(BaseRepository):
    """
    Repository for item operations.

    This class provides database access functions for item operations.
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: Database session
        """
        super().__init__(session)

    def get_by_id(self, item_id: str | uuid.UUID) -> Optional[Item]:
        """
        Get an item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item if found, None otherwise
        """
        return self.get(Item, item_id)

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[uuid.UUID] = None,
    ) -> List[Item]:
        """
        Get multiple items with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            owner_id: Filter by owner ID if provided

        Returns:
            List of items
        """
        statement = select(Item)

        if owner_id:
            statement = statement.where(col(Item.owner_id) == owner_id)

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement))

    def create(self, item: Item) -> Item:
        """
        Create a new item.

        Args:
            item: Item to create

        Returns:
            Created item
        """
        return super().create(item)

    def update(self, item: Item) -> Item:
        """
        Update an existing item.

        Args:
            item: Item to update

        Returns:
            Updated item
        """
        return super().update(item)

    def delete(self, item: Item) -> None:
        """
        Delete an item.

        Args:
            item: Item to delete
        """
        super().delete(item)

    def count(self, owner_id: Optional[uuid.UUID] = None) -> int:
        """
        Count items.

        Args:
            owner_id: Filter by owner ID if provided

        Returns:
            Number of items
        """
        statement = select(Item)

        if owner_id:
            statement = statement.where(col(Item.owner_id) == owner_id)

        return len(self.session.exec(statement).all())

    def exists_by_id(self, item_id: str | uuid.UUID) -> bool:
        """
        Check if an item exists by ID.

        Args:
            item_id: Item ID

        Returns:
            True if item exists, False otherwise
        """
        statement = select(Item).where(col(Item.id) == item_id)
        return self.session.exec(statement).first() is not None

    def is_owned_by(self, item_id: str | uuid.UUID, owner_id: str | uuid.UUID) -> bool:
        """
        Check if an item is owned by a user.

        Args:
            item_id: Item ID
            owner_id: Owner ID

        Returns:
            True if item is owned by user, False otherwise
        """
        statement = select(Item).where(
            (col(Item.id) == item_id) & (col(Item.owner_id) == owner_id)
        )
        return self.session.exec(statement).first() is not None