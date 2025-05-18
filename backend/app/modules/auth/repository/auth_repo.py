"""
Auth repository.

This module provides database access functions for authentication operations.
"""
from sqlmodel import Session, select

from app.core.db import BaseRepository
from app.models import User  # Temporary import until User module is extracted


class AuthRepository(BaseRepository):
    """
    Repository for authentication operations.
    
    This class provides database access functions for authentication operations.
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: Database session
        """
        super().__init__(session)
    
    def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def verify_user_exists(self, user_id: str) -> bool:
        """
        Verify that a user exists by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user exists, False otherwise
        """
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None
    
    def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: User ID
            hashed_password: Hashed password
            
        Returns:
            True if update was successful, False otherwise
        """
        user = self.session.get(User, user_id)
        if not user:
            return False
        
        user.hashed_password = hashed_password
        self.session.add(user)
        self.session.commit()
        return True