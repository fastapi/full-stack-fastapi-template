from fastapi import APIRouter
import logging
from app.api.routes import user_prompts, auth
from app.api.routes import profile
from app.api.routes import dashboard
from app.api.routes import projects
from app.api.routes import webhooks
from app.config import settings


api_router = APIRouter()
api_router.include_router(user_prompts.router, tags=["prompts"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(webhooks.router, tags=["webhooks"])


# Private routes router (e.g., for debugging)
private_router = APIRouter(prefix="/debug", tags=["debug"])


@private_router.get("/health")
def health_check():
    return {"status": "ok"}


if settings.environment == "development":
    api_router.include_router(private_router)
