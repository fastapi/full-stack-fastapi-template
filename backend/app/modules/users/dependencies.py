"""
User module dependencies.

This module provides dependencies for the user module.
"""
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import CurrentUser
from app.core.db import get_repository, get_session
# Import User from the users module
from app.modules.users.domain.models import User
from app.modules.users.repository.user_repo import UserRepository
from app.modules.users.services.user_service import UserService


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    """
    Get a user repository instance.

    Args:
        session: Database session

    Returns:
        User repository instance
    """
    return UserRepository(session)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Get a user service instance.

    Args:
        user_repo: User repository

    Returns:
        User service instance
    """
    return UserService(user_repo)


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Get the current active superuser.

    Args:
        current_user: Current user

    Returns:
        Current user if superuser

    Raises:
        HTTPException: If not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# Alternative using the repository factory
get_user_repo = get_repository(UserRepository)