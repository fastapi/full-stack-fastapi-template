"""
Auth module dependencies.

This module provides dependencies for the auth module.
"""
from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_repository, get_session
from app.modules.auth.repository.auth_repo import AuthRepository
from app.modules.auth.services.auth_service import AuthService


def get_auth_repository(session: Session = Depends(get_session)) -> AuthRepository:
    """
    Get an auth repository instance.
    
    Args:
        session: Database session
        
    Returns:
        Auth repository instance
    """
    return AuthRepository(session)


def get_auth_service(
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    """
    Get an auth service instance.
    
    Args:
        auth_repo: Auth repository
        
    Returns:
        Auth service instance
    """
    return AuthService(auth_repo)


# Alternative using the repository factory
get_auth_repo = get_repository(AuthRepository)