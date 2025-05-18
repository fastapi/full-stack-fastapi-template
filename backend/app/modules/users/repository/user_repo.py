"""
User repository.

This module provides database access functions for user operations.
"""
import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.core.db import BaseRepository
from app.modules.users.domain.models import User


class UserRepository(BaseRepository):
    """
    Repository for user operations.
    
    This class provides database access functions for user operations.
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: Database session
        """
        super().__init__(session)
    
    def get_by_id(self, user_id: str | uuid.UUID) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return self.get(User, user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[User]:
        """
        Get multiple users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only include active users if True
            
        Returns:
            List of users
        """
        statement = select(User)
        
        if active_only:
            statement = statement.where(User.is_active == True)
            
        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement))
    
    def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User to create
            
        Returns:
            Created user
        """
        return super().create(user)
    
    def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user: User to update
            
        Returns:
            Updated user
        """
        return super().update(user)
    
    def delete(self, user: User) -> None:
        """
        Delete a user.
        
        Args:
            user: User to delete
        """
        super().delete(user)
    
    def count(self, active_only: bool = True) -> int:
        """
        Count users.
        
        Args:
            active_only: Only count active users if True
            
        Returns:
            Number of users
        """
        statement = select(User)
        
        if active_only:
            statement = statement.where(User.is_active == True)
        
        return len(self.session.exec(statement).all())
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists by email.
        
        Args:
            email: User email
            
        Returns:
            True if user exists, False otherwise
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first() is not None