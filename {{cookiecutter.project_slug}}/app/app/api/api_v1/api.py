from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, utils

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
