from fastapi import APIRouter

from app.api.routes import clubs, items, login, movies, private, ratings, users, utils, watchlist
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(movies.router)
api_router.include_router(watchlist.router)
api_router.include_router(ratings.router)
api_router.include_router(clubs.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
