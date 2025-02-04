from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, paths, learn
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(paths.router)
api_router.include_router(learn.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
