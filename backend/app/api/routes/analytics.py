from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/")
async def get_analytics(current_user: CurrentUser, session: SessionDep):
    """Obtener analytics"""
    return {
        "message": "Analytics endpoint",
        "user": current_user,
        "analytics": {}
    } 