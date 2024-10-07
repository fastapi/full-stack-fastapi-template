from fastapi import APIRouter

from app.api.routes import items, login, users, utils

# Create a main APIRouter instance
api_router = APIRouter()

# Include the login router without a prefix, tagged as "login"
api_router.include_router(login.router, tags=["login"])

# Include the users router with "/users" prefix, tagged as "users"
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include the utils router with "/utils" prefix, tagged as "utils"
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

api_router.include_router(items.router, prefix="/items", tags=["items"])
