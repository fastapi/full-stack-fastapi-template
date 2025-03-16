import uuid
from typing import Any, Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.repositories.user import UserRepository


# Create a singleton instance of the repository
user_repository = UserRepository()


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        session: Database session
        user_create: User create schema
        
    Returns:
        Created user
    """
    return user_repository.create(session=session, obj_in=user_create)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """
    Update a user in the database.
    
    Args:
        session: Database session
        db_user: Existing user object
        user_in: User update schema
        
    Returns:
        Updated user
    """
    return user_repository.update(session=session, db_obj=db_user, obj_in=user_in)


def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        session: Database session
        email: User email
        
    Returns:
        User if found, None otherwise
    """
    return user_repository.get_by_email(session=session, email=email)


def authenticate(*, session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        session: Database session
        email: User email
        password: User password
        
    Returns:
        User if authentication succeeded, None otherwise
    """
    return user_repository.authenticate(session=session, email=email, password=password)


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        session: Database session
        user_id: User ID
        
    Returns:
        User if found, None otherwise
    """
    return user_repository.get(session=session, id=user_id)


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a list of users.
    
    Args:
        session: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users
    """
    return user_repository.get_multi(session=session, skip=skip, limit=limit)


def is_active(user: User) -> bool:
    """Check if a user is active."""
    return user.is_active


def is_superuser(user: User) -> bool:
    """Check if a user is a superuser."""
    return user.is_superuser 