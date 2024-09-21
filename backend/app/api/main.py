from fastapi import APIRouter

from app.api.routes import venues

api_router = APIRouter()
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])

