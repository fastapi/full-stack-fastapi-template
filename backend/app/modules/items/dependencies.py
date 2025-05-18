"""
Item module dependencies.

This module provides dependencies for the item module.
"""
from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_repository, get_session
from app.modules.items.repository.item_repo import ItemRepository
from app.modules.items.services.item_service import ItemService


def get_item_repository(session: Session = Depends(get_session)) -> ItemRepository:
    """
    Get an item repository instance.
    
    Args:
        session: Database session
        
    Returns:
        Item repository instance
    """
    return ItemRepository(session)


def get_item_service(
    item_repo: ItemRepository = Depends(get_item_repository),
) -> ItemService:
    """
    Get an item service instance.
    
    Args:
        item_repo: Item repository
        
    Returns:
        Item service instance
    """
    return ItemService(item_repo)


# Alternative using the repository factory
get_item_repo = get_repository(ItemRepository)