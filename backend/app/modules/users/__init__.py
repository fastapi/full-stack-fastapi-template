"""
Users module initialization.

This module handles user management operations.
"""
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.db import session_manager
from app.core.logging import get_logger


# Configure logger
logger = get_logger("users_module")


def get_users_router() -> APIRouter:
    """
    Get the users module's router.

    Returns:
        APIRouter for users module
    """
    from app.modules.users.api.routes import router as users_router
    return users_router


def init_users_module(app: FastAPI) -> None:
    """
    Initialize the users module.

    This function sets up routes and event handlers for the users module.

    Args:
        app: FastAPI application
    """
    from app.modules.users.api.routes import router as users_router
    from app.modules.users.repository.user_repo import UserRepository
    from app.modules.users.services.user_service import UserService

    # Include the users router in the application
    app.include_router(users_router, prefix=settings.API_V1_STR)

    # Set up any event handlers or startup tasks for the users module
    @app.on_event("startup")
    async def init_users():
        """Initialize users module on application startup."""
        # Create initial superuser if it doesn't exist
        with session_manager() as session:
            user_repo = UserRepository(session)
            user_service = UserService(user_repo)
            superuser = user_service.create_initial_superuser()

            if superuser:
                logger.info(
                    f"Created initial superuser with email: {superuser.email}"
                )
            else:
                logger.info("Initial superuser already exists")