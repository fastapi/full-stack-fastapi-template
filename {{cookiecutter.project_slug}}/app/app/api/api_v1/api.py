from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
