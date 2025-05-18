"""
Auth module initialization.

This module handles authentication and authorization operations.
"""
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import get_logger

# Configure logger
logger = get_logger("auth_module")


def get_auth_router() -> APIRouter:
    """
    Get the auth module's router.
    
    Returns:
        APIRouter for auth module
    """
    # Import here to avoid circular imports
    from app.modules.auth.api.routes import router as auth_router
    return auth_router


def init_auth_module(app: FastAPI) -> None:
    """
    Initialize the auth module.
    
    This function sets up routes and event handlers for the auth module.
    
    Args:
        app: FastAPI application
    """
    # Import here to avoid circular imports
    from app.modules.auth.api.routes import router as auth_router
    
    # Include the auth router in the application
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    
    # Set up any event handlers or startup tasks for the auth module
    @app.on_event("startup")
    async def init_auth():
        """Initialize auth module on application startup."""
        logger.info("Auth module initialized")