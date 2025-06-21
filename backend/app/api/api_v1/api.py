from app.api.api_v1.endpoints import login
api_router.include_router(login.router, prefix="/auth", tags=["auth"])
