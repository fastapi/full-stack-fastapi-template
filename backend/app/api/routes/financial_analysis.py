from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/financial-analysis", tags=["financial-analysis"])

@router.get("/")
async def get_financial_analysis(current_user: CurrentUser, session: SessionDep):
    """Obtener análisis financiero"""
    return {
        "message": "Financial analysis endpoint",
        "user": current_user,
        "analysis": {}
    } 