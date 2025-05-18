"""
Common dependencies for the API.

This module provides common dependencies that can be used across all API routes.
"""
from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.core.logging import get_logger
from app.core.security import ALGORITHM, decode_access_token
from app.shared.exceptions import AuthenticationException, PermissionException

# Temporary imports until modules are ready - use legacy models
from app.models import TokenPayload, User

# Initialize logger
logger = get_logger("api.deps")

# OAuth2 scheme for token authentication
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    This is a temporary compatibility function that will be removed
    once all code is migrated to use get_session from app.core.db.
    
    Yields:
        Database session
    """
    yield from get_session()


# Type dependencies
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Get the current authenticated user based on JWT token.
    
    Args:
        session: Database session
        token: JWT token
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = decode_access_token(token)
        token_data = TokenPayload.model_validate(payload)
        if not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (InvalidTokenError, ValidationError) as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    # Get user from database using legacy model for now
    user = session.get(User, token_data.sub)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Get the current active superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current active superuser
        
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]