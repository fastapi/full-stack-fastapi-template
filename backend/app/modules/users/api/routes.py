"""
User routes.

This module provides API routes for user operations.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, CurrentSuperuser, SessionDep
from app.core.config import settings
from app.core.logging import get_logger
from app.models import Message  # Temporary import until Message is moved to shared
from app.modules.users.dependencies import get_user_service
from app.modules.users.domain.models import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.modules.users.services.user_service import UserService
from app.shared.exceptions import NotFoundException, ValidationException

# Configure logger
logger = get_logger("user_routes")

# Create router
router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(CurrentSuperuser)],
    response_model=UsersPublic,
)
def read_users(
    skip: int = 0, 
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Retrieve users.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_service: User service
        
    Returns:
        List of users
    """
    users, count = user_service.get_users(skip=skip, limit=limit)
    return user_service.to_public_list(users, count)


@router.post(
    "/", 
    dependencies=[Depends(CurrentSuperuser)], 
    response_model=UserPublic,
)
def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Create new user.
    
    Args:
        user_in: User creation data
        user_service: User service
        
    Returns:
        Created user
    """
    try:
        user = user_service.create_user(user_in)
        
        # Send email notification if enabled
        if settings.emails_enabled and user_in.email:
            # This will be handled by email module in future
            # For now, just log that an email would be sent
            logger.info(f"New account email would be sent to: {user_in.email}")
            
        return user_service.to_public(user)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    user_in: UserUpdateMe,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Update own user.
    
    Args:
        user_in: User update data
        current_user: Current user
        user_service: User service
        
    Returns:
        Updated user
    """
    try:
        user = user_service.update_user_me(current_user, user_in)
        return user_service.to_public(user)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.patch("/me/password", response_model=Message)
def update_password_me(
    body: UpdatePassword,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Update own password.
    
    Args:
        body: Password update data
        current_user: Current user
        user_service: User service
        
    Returns:
        Success message
    """
    try:
        if body.current_password == body.new_password:
            raise ValidationException(
                detail="New password cannot be the same as the current one"
            )
            
        user_service.update_password(
            current_user, body.current_password, body.new_password
        )
        
        return Message(message="Password updated successfully")
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserPublic)
def read_user_me(
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current user
        user_service: User service
        
    Returns:
        Current user
    """
    return user_service.to_public(current_user)


@router.delete("/me", response_model=Message)
def delete_user_me(
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Delete own user.
    
    Args:
        current_user: Current user
        user_service: User service
        
    Returns:
        Success message
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
        
    user_service.delete_user(current_user.id)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(
    user_in: UserRegister,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Create new user without the need to be logged in.
    
    Args:
        user_in: User registration data
        user_service: User service
        
    Returns:
        Created user
    """
    try:
        user = user_service.register_user(user_in)
        return user_service.to_public(user)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Get a specific user by id.
    
    Args:
        user_id: User ID
        current_user: Current user
        user_service: User service
        
    Returns:
        User
    """
    try:
        user = user_service.get_user(user_id)
        
        # Check permissions
        if user.id == current_user.id:
            return user_service.to_public(user)
            
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privileges",
            )
            
        return user_service.to_public(user)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{user_id}",
    dependencies=[Depends(CurrentSuperuser)],
    response_model=UserPublic,
)
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Update a user.
    
    Args:
        user_id: User ID
        user_in: User update data
        user_service: User service
        
    Returns:
        Updated user
    """
    try:
        user = user_service.update_user(user_id, user_in)
        return user_service.to_public(user)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{user_id}", 
    dependencies=[Depends(CurrentSuperuser)],
    response_model=Message,
)
def delete_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Delete a user.
    
    Args:
        user_id: User ID
        current_user: Current user
        user_service: User service
        
    Returns:
        Success message
    """
    try:
        if str(user_id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super users are not allowed to delete themselves",
            )
            
        user_service.delete_user(user_id)
        return Message(message="User deleted successfully")
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )