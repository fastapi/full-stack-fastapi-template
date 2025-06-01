from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, events, speeches # Added events, speeches
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router) # No prefix, tags=['login'] typically
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"]) # Assuming utils has a prefix
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(events.router, prefix="/events", tags=["events"]) # Added
api_router.include_router(speeches.router, prefix="/speeches", tags=["speeches"]) # Added


if settings.ENVIRONMENT == "local":
    # Assuming private router also has a prefix if it's for specific resources
    api_router.include_router(private.router, prefix="/private", tags=["private"])
