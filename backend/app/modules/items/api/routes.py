"""
Item routes.

This module provides API routes for item operations.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, CurrentSuperuser, SessionDep
from app.core.logging import get_logger
from app.models import Message  # Temporary import until Message is moved to shared
from app.modules.items.dependencies import get_item_service
from app.modules.items.domain.models import (
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.modules.items.services.item_service import ItemService
from app.shared.exceptions import NotFoundException, PermissionException

# Configure logger
logger = get_logger("item_routes")

# Create router
router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    skip: int = 0, 
    limit: int = 100,
    current_user: CurrentUser = Depends(),
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Retrieve items.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current user
        item_service: Item service
        
    Returns:
        List of items
    """
    if current_user.is_superuser:
        # Superusers can see all items
        items, count = item_service.get_items(skip=skip, limit=limit)
    else:
        # Regular users can only see their own items
        items, count = item_service.get_user_items(
            owner_id=current_user.id, skip=skip, limit=limit
        )
    
    return item_service.to_public_list(items, count)


@router.get("/{item_id}", response_model=ItemPublic)
def read_item(
    item_id: uuid.UUID,
    current_user: CurrentUser = Depends(),
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Get item by ID.
    
    Args:
        item_id: Item ID
        current_user: Current user
        item_service: Item service
        
    Returns:
        Item
    """
    try:
        item = item_service.get_item(item_id)
        
        # Check permissions
        if not current_user.is_superuser and (item.owner_id != current_user.id):
            logger.warning(
                f"User {current_user.id} attempted to access item {item_id} "
                f"owned by {item.owner_id}"
            )
            raise PermissionException(detail="Not enough permissions")
            
        return item_service.to_public(item)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/", response_model=ItemPublic)
def create_item(
    item_in: ItemCreate,
    current_user: CurrentUser = Depends(),
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Create new item.
    
    Args:
        item_in: Item creation data
        current_user: Current user
        item_service: Item service
        
    Returns:
        Created item
    """
    item = item_service.create_item(
        owner_id=current_user.id, item_create=item_in
    )
    
    return item_service.to_public(item)


@router.put("/{item_id}", response_model=ItemPublic)
def update_item(
    item_id: uuid.UUID,
    item_in: ItemUpdate,
    current_user: CurrentUser = Depends(),
    item_service: ItemService = Depends(get_item_service),
) -> Any:
    """
    Update an item.
    
    Args:
        item_id: Item ID
        item_in: Item update data
        current_user: Current user
        item_service: Item service
        
    Returns:
        Updated item
    """
    try:
        # Superusers can update any item, regular users only their own
        enforce_ownership = not current_user.is_superuser
        
        item = item_service.update_item(
            item_id=item_id,
            owner_id=current_user.id,
            item_update=item_in,
            enforce_ownership=enforce_ownership,
        )
        
        return item_service.to_public(item)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{item_id}")
def delete_item(
    item_id: uuid.UUID,
    current_user: CurrentUser = Depends(),
    item_service: ItemService = Depends(get_item_service),
) -> Message:
    """
    Delete an item.
    
    Args:
        item_id: Item ID
        current_user: Current user
        item_service: Item service
        
    Returns:
        Success message
    """
    try:
        # Superusers can delete any item, regular users only their own
        enforce_ownership = not current_user.is_superuser
        
        item_service.delete_item(
            item_id=item_id,
            owner_id=current_user.id,
            enforce_ownership=enforce_ownership,
        )
        
        return Message(message="Item deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )