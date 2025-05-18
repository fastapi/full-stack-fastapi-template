"""
API routes registration and initialization.

This module handles the registration of all API routes and module initialization.
"""
from fastapi import FastAPI, APIRouter

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.auth import init_auth_module
from app.modules.email import init_email_module
from app.modules.items import init_items_module
from app.modules.users import init_users_module
from app.modules.utils import init_utils_module

# Initialize logger
logger = get_logger("api.main")

# Create the main API router
api_router = APIRouter()


def init_api_routes(app: FastAPI) -> None:
    """
    Initialize API routes.

    This function registers all module routers and initializes the modules.

    Args:
        app: FastAPI application
    """
    # Include the API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Initialize all modules
    init_auth_module(app)
    init_users_module(app)
    init_items_module(app)
    init_email_module(app)
    init_utils_module(app)

    logger.info("API routes initialized")