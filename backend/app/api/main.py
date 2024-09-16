from app.api.routes import items, utils
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
