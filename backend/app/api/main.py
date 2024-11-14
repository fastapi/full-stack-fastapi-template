# This script sets up the main API router for the FastAPI application, organizing and including various sub-routers to handle specific sections of the API. Each sub-router, defined in separate route modules (items, login, users, utils, and geospatial), corresponds to different functional areas of the application, such as user management, item handling, utility functions, and geospatial data handling. By consolidating these routers under the main api_router, this script provides a centralized routing structure, enabling modular API section management and streamlined route access for the application’s endpoints.

# Import APIRouter from FastAPI and the other route modules
from fastapi import APIRouter

# Import the other route modules
from app.api.routes import items, login, users, utils, geospatial

# Initialize the main API router
api_router = APIRouter()

# Include routers for different API sections
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(geospatial.router, prefix="/geospatial", tags=["geospatial"])