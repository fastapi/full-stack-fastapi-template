from fastapi import APIRouter

from app.api.routes import venues, menu, users, login


api_router = APIRouter()
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
