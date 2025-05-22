from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.api.routes.auth.router import router as auth_router
from app.core.config import settings

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix=settings.API_V1_STR)

# Include other routes
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])

# Include private routes in local environment
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router, tags=["private"])
