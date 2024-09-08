from fastapi import APIRouter

from app.api.routes import users, utils, auth, lookup, resume

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["lookup"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])


