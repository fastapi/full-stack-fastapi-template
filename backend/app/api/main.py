from fastapi import APIRouter

from app.api.routes import (
    generate,
    generations,
    items,
    login,
    private,
    templates,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(templates.router)
api_router.include_router(generate.router)
api_router.include_router(generations.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
