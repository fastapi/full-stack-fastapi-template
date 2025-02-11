from fastapi import APIRouter

from app.auth import routes as auth_routes
from app.core.config import settings
from app.items import routes as items_routes
from app.users import private_routes as users_private_routes
from app.users import routes as users_routes
from app.utils import routes as utils_routes

api_router = APIRouter()
api_router.include_router(items_routes.router)
api_router.include_router(auth_routes.router)
api_router.include_router(utils_routes.router)
api_router.include_router(users_routes.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(users_private_routes.router)
