"""
Shared utility functions for the application.

This module contains utility functions used across multiple modules.
"""
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypeVar, Union

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlmodel import Session, select

from app.shared.exceptions import NotFoundException

T = TypeVar("T")


def create_response_model(items: List[T], count: int) -> Dict[str, Any]:
    """
    Create a standard response model for collections with pagination info.
    
    Args:
        items: List of items to include in response
        count: Total number of items available
        
    Returns:
        Dict with data and count keys
    """
    return {
        "data": items,
        "count": count
    }


def get_utc_now() -> datetime:
    """Get the current UTC datetime."""
    return datetime.now(timezone.utc)


def uuid_to_str(uuid_obj: Union[uuid.UUID, str, None]) -> Optional[str]:
    """
    Convert a UUID object to a string.
    
    Args:
        uuid_obj: UUID object or string
        
    Returns:
        String representation of UUID or None if input is None
    """
    if uuid_obj is None:
        return None
    
    if isinstance(uuid_obj, uuid.UUID):
        return str(uuid_obj)
    
    return uuid_obj


def validate_uuid(value: str) -> bool:
    """
    Validate that a string is a valid UUID.
    
    Args:
        value: String to validate
        
    Returns:
        True if value is a valid UUID, False otherwise
    """
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def get_or_404(session: Session, model: Any, id: Union[UUID4, str]) -> Any:
    """
    Get a database object by ID or raise a 404 exception.
    
    Args:
        session: Database session
        model: SQLModel class
        id: ID of the object to retrieve
        
    Returns:
        Database object
        
    Raises:
        NotFoundException: If object does not exist
    """
    obj = session.get(model, id)
    if not obj:
        raise NotFoundException(f"{model.__name__} with id {id} not found")
    return obj


def is_valid_email(email: str) -> bool:
    """
    Validate email format using a simple regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))