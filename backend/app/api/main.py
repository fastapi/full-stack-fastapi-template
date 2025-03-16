from fastapi import APIRouter

from app.api.api_v1.api import api_router as api_v1_router
from app.core.config import settings

# Main API router that includes version-specific routers
api_router = APIRouter()

# Include the v1 API router without an additional prefix
# The /v1 prefix is handled in app.main.py with settings.API_V1_STR
api_router.include_router(api_v1_router)

