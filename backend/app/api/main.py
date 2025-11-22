from fastapi import APIRouter

from app.api.routes import admin, document_lifecycle, documents, items, login, private, users, utils, version_management, workflows
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(document_lifecycle.router, prefix="/documents", tags=["lifecycle"])
api_router.include_router(version_management.router, prefix="/documents", tags=["versions"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(admin.router, prefix="/admin/documents", tags=["admin"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
