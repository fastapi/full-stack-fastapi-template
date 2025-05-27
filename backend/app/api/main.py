from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, mcp
from app.api.routes.auth.router import router as auth_router
from app.core.config import settings

api_router = APIRouter()

# Include auth routes - already prefixed with /api/v1 in main.py
api_router.include_router(auth_router)

# Include other routes - they will be under /api/v1 prefix added in main.py
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# Include private routes in local environment
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router, prefix="/private", tags=["private"])
