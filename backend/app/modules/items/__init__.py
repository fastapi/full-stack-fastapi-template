"""
Items module initialization.

This module handles item management operations.
"""
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import get_logger

# Configure logger
logger = get_logger("items_module")


def get_items_router() -> APIRouter:
    """
    Get the items module's router.

    Returns:
        APIRouter for items module
    """
    from app.modules.items.api.routes import router as items_router
    return items_router


def init_items_module(app: FastAPI) -> None:
    """
    Initialize the items module.

    This function sets up routes and event handlers for the items module.

    Args:
        app: FastAPI application
    """
    from app.modules.items.api.routes import router as items_router

    # Include the items router in the application
    app.include_router(items_router, prefix=settings.API_V1_STR)

    # Set up any event handlers or startup tasks for the items module
    @app.on_event("startup")
    async def init_items():
        """Initialize items module on application startup."""
        logger.info("Items module initialized")