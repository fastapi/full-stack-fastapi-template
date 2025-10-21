from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, projects, galleries
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(galleries.router, prefix="/galleries", tags=["galleries"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
 