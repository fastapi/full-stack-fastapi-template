from fastapi import APIRouter

from app.api.routes import (
    documents,
    exam_attempts,
    exams,
    items,
    login,
    private,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(exams.router)
api_router.include_router(exam_attempts.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
