from fastapi import APIRouter

from app.api.routes import articles, items, likes, login, private, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(articles.router)
api_router.include_router(likes.router)


if settings.ENVIRONMENT == "development":
    api_router.include_router(private.router)
