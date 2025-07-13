from fastapi import APIRouter

from app.api.routes import (
    ai_souls,
    chat,
    counselor,
    documents,
    enhanced_rag,
    items,
    login,
    private,
    training,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(private.router, prefix="/private", tags=["private"])
api_router.include_router(ai_souls.router, prefix="/ai-souls", tags=["ai-souls"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(counselor.router, prefix="/counselor", tags=["counselor"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(enhanced_rag.router, prefix="/rag", tags=["enhanced-rag"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
