from fastapi import APIRouter

from app.api.routes import items, login, private, social, users, utils, workouts, p_bests, auth, admin
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(social.router)
api_router.include_router(workouts.router)
api_router.include_router(p_bests.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
