from fastapi import APIRouter

from app.api.routes import (
    items,
    login,
    private,
    users,
    utils,
    # Inventory management routes
    categories,
    products,
    inventory_movements,
    alerts,
    kardex,
    reports,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)

# Inventory management endpoints
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(inventory_movements.router)
api_router.include_router(alerts.router)
api_router.include_router(kardex.router)
api_router.include_router(reports.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
