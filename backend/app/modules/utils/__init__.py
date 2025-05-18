"""
Utils module initialization.

This module provides utility endpoints and functions.
"""
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import get_logger

# Configure logger
logger = get_logger("utils_module")


def get_utils_router() -> APIRouter:
    """
    Get the utils module's router.

    Returns:
        APIRouter for utils module
    """
    from app.modules.utils.api.routes import router as utils_router
    return utils_router


def init_utils_module(app: FastAPI) -> None:
    """
    Initialize the utils module.

    This function sets up routes for the utils module.

    Args:
        app: FastAPI application
    """
    from app.modules.utils.api.routes import router as utils_router

    # Include the utils router in the application
    app.include_router(utils_router, prefix=settings.API_V1_STR)

    # Log initialization
    logger.info("Utils module initialized")
