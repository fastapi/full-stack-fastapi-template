from fastapi import APIRouter

from app.api.routes import (
    comments,
    galleries,
    invitations,
    login,
    organizations,
    private,
    project_access,
    projects,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)


api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)

api_router.include_router(
    project_access.router, prefix="/projects", tags=["project-access"]
)

api_router.include_router(comments.router, prefix="/comments", tags=["comments"])

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

api_router.include_router(
    invitations.router, prefix="/invitations", tags=["invitations"]
)

api_router.include_router(galleries.router, prefix="/galleries", tags=["galleries"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
