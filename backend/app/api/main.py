from fastapi import APIRouter

from app.api.routes import venues, menu, users, login,qrcode


api_router = APIRouter()
api_router.include_router(venues.router, prefix="/venue", tags=["venue"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(users.router, prefix="/user", tags=["user"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(qrcode.router, tags=["qrcode"])
