from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, metrics, sentences, memory
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(sentences.router, prefix="/sentences", tags=["sentences"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
