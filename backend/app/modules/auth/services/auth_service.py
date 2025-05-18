"""
Auth service.

This module provides business logic for authentication operations.
"""
from datetime import timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from pydantic import EmailStr

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    get_password_hash,
    generate_password_reset_token,
    verify_password,
    verify_password_reset_token,
)
from app.models import User  # Temporary import until User module is extracted
from app.modules.auth.domain.models import Token
from app.modules.auth.repository.auth_repo import AuthRepository
from app.shared.exceptions import AuthenticationException, NotFoundException

# Configure logger
logger = get_logger("auth_service")


class AuthService:
    """
    Service for authentication operations.
    
    This class provides business logic for authentication operations.
    """
    
    def __init__(self, auth_repo: AuthRepository):
        """
        Initialize service with auth repository.
        
        Args:
            auth_repo: Auth repository
        """
        self.auth_repo = auth_repo
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User if authentication is successful, None otherwise
        """
        user = self.auth_repo.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_access_token_for_user(
        self, user: User, expires_delta: Optional[timedelta] = None
    ) -> Token:
        """
        Create an access token for a user.
        
        Args:
            user: User to create token for
            expires_delta: Token expiration time
            
        Returns:
            Token object
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(
            subject=user.id, expires_delta=expires_delta
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def login(self, email: str, password: str) -> Token:
        """
        Login a user and return an access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Token object
            
        Raises:
            AuthenticationException: If login fails
        """
        user = self.authenticate_user(email, password)
        
        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            raise AuthenticationException(detail="Incorrect email or password")
        
        return self.create_access_token_for_user(user)
    
    def request_password_reset(self, email: EmailStr) -> bool:
        """
        Request a password reset.
        
        Args:
            email: User email
            
        Returns:
            True if request was successful, False if user not found
        """
        user = self.auth_repo.get_user_by_email(email)
        
        if not user:
            # Don't reveal that the user doesn't exist for security
            return False
        
        # Generate password reset token
        password_reset_token = generate_password_reset_token(email=email)
        
        # Event should be published here to notify email service to send password reset email
        # self.event_publisher.publish_event(
        #     PasswordResetRequested(
        #         email=email,
        #         token=password_reset_token
        #     )
        # )
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            True if reset was successful
            
        Raises:
            AuthenticationException: If token is invalid
            NotFoundException: If user not found
        """
        email = verify_password_reset_token(token)
        
        if not email:
            raise AuthenticationException(detail="Invalid or expired token")
        
        user = self.auth_repo.get_user_by_email(email)
        
        if not user:
            raise NotFoundException(detail="User not found")
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update user password
        success = self.auth_repo.update_user_password(
            user_id=str(user.id), hashed_password=hashed_password
        )
        
        if not success:
            logger.error(f"Failed to update password for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )
        
        return success