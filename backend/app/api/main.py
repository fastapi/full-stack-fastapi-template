from fastapi import APIRouter

from app.api.routes import ingestions, login, private, tasks, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(tasks.router)
api_router.include_router(ingestions.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
