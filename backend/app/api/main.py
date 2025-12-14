from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.core.config import settings
from app.premium_users import routes as premium_routes

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(premium_routes.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
