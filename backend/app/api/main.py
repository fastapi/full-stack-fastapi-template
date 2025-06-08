from fastapi import APIRouter

from app.api.routes import items, login, private, social, users, utils, workouts, notifications
from app.core.config import settings
from app.api.routes import p_bests

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(social.router)
api_router.include_router(workouts.router)
api_router.include_router(p_bests.router)
api_router.include_router(notifications.router, prefix="/notifications")

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
