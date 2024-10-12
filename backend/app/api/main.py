from fastapi import APIRouter

from app.api.routes import venues, menu, users, login, qrcode, carousel


api_router = APIRouter()
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(qrcode.router, tags=["qrcode"])
api_router.include_router(carousel.router, prefix="/carousel", tags=["carousel"])
