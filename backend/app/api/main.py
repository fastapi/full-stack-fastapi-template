from fastapi import APIRouter

from app.api.routes import entities

api_router = APIRouter()
api_router.include_router(entities.router)
