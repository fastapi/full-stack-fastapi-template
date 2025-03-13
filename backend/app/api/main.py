from fastapi import APIRouter

from app.api.api_v1.api import api_router as v1_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(v1_router)

