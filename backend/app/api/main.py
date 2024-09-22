from fastapi import APIRouter

from app.api.routes import venues
from app.api.routes import menu

api_router = APIRouter()
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
