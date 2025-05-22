from fastapi import APIRouter

from app.api.routes.auth import auth, oauth

router = APIRouter()

# Include auth routes
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include OAuth/SSO routes
router.include_router(oauth.router, tags=["oauth"])
