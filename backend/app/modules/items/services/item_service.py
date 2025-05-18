"""
Item service.

This module provides business logic for item operations.
"""
import uuid
from typing import List, Optional, Tuple

from app.core.logging import get_logger
from app.modules.items.domain.models import (
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.modules.items.repository.item_repo import ItemRepository
from app.shared.exceptions import NotFoundException, PermissionException

# Configure logger
logger = get_logger("item_service")


class ItemService:
    """
    Service for item operations.

    This class provides business logic for item operations.
    """

    def __init__(self, item_repo: ItemRepository):
        """
        Initialize service with item repository.

        Args:
            item_repo: Item repository
        """
        self.item_repo = item_repo

    def get_item(self, item_id: str | uuid.UUID) -> Item:
        """
        Get an item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item

        Raises:
            NotFoundException: If item not found
        """
        item = self.item_repo.get_by_id(item_id)

        if not item:
            raise NotFoundException(message=f"Item with ID {item_id} not found")

        return item

    def get_items(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[uuid.UUID] = None,
    ) -> Tuple[List[Item], int]:
        """
        Get multiple items with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            owner_id: Filter by owner ID if provided

        Returns:
            Tuple of (list of items, total count)
        """
        items = self.item_repo.get_multi(
            skip=skip, limit=limit, owner_id=owner_id
        )
        count = self.item_repo.count(owner_id=owner_id)

        return items, count

    def get_user_items(
        self,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Item], int]:
        """
        Get items belonging to a user.

        Args:
            owner_id: Owner ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of items, total count)
        """
        return self.get_items(skip=skip, limit=limit, owner_id=owner_id)

    def create_item(self, owner_id: uuid.UUID, item_create: ItemCreate) -> Item:
        """
        Create a new item.

        Args:
            owner_id: Owner ID
            item_create: Item creation data

        Returns:
            Created item
        """
        item = Item(
            title=item_create.title,
            description=item_create.description,
            owner_id=owner_id,
        )

        return self.item_repo.create(item)

    def update_item(
        self,
        item_id: str | uuid.UUID,
        owner_id: uuid.UUID,
        item_update: ItemUpdate,
        enforce_ownership: bool = True,
    ) -> Item:
        """
        Update an item.

        Args:
            item_id: Item ID
            owner_id: Owner ID
            item_update: Item update data
            enforce_ownership: Whether to check if the user owns the item

        Returns:
            Updated item

        Raises:
            NotFoundException: If item not found
            PermissionException: If user does not own the item
        """
        # Get existing item
        item = self.get_item(item_id)

        # Check ownership
        if enforce_ownership and item.owner_id != owner_id:
            logger.warning(
                f"User {owner_id} attempted to update item {item_id} "
                f"owned by {item.owner_id}"
            )
            raise PermissionException(message="Not enough permissions")

        # Update fields
        if item_update.title is not None:
            item.title = item_update.title

        if item_update.description is not None:
            item.description = item_update.description

        return self.item_repo.update(item)

    def delete_item(
        self,
        item_id: str | uuid.UUID,
        owner_id: uuid.UUID,
        enforce_ownership: bool = True,
    ) -> None:
        """
        Delete an item.

        Args:
            item_id: Item ID
            owner_id: Owner ID
            enforce_ownership: Whether to check if the user owns the item

        Raises:
            NotFoundException: If item not found
            PermissionException: If user does not own the item
        """
        # Get existing item
        item = self.get_item(item_id)

        # Check ownership
        if enforce_ownership and item.owner_id != owner_id:
            logger.warning(
                f"User {owner_id} attempted to delete item {item_id} "
                f"owned by {item.owner_id}"
            )
            raise PermissionException(message="Not enough permissions")

        # Delete item
        self.item_repo.delete(item)

    def check_ownership(self, item_id: str | uuid.UUID, owner_id: uuid.UUID) -> bool:
        """
        Check if a user owns an item.

        Args:
            item_id: Item ID
            owner_id: Owner ID

        Returns:
            True if user owns the item, False otherwise
        """
        return self.item_repo.is_owned_by(item_id, owner_id)

    # Public model conversions

    def to_public(self, item: Item) -> ItemPublic:
        """
        Convert item to public model.

        Args:
            item: Item to convert

        Returns:
            Public item
        """
        return ItemPublic.model_validate(item)

    def to_public_list(self, items: List[Item], count: int) -> ItemsPublic:
        """
        Convert list of items to public model.

        Args:
            items: Items to convert
            count: Total count

        Returns:
            Public items list
        """
        return ItemsPublic(
            data=[self.to_public(item) for item in items],
            count=count,
        )