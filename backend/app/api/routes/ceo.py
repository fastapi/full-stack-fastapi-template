from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/ceo", tags=["ceo"])


@router.get("/dashboard")
async def get_ceo_dashboard(current_user: CurrentUser, session: SessionDep):
    """Dashboard del CEO"""
    return {
        "message": "CEO Dashboard",
        "user": current_user,
        "stats": {
            "total_users": 0,
            "total_properties": 0,
            "total_revenue": 0,
            "active_branches": 0
        }
    }


@router.get("/analytics")
async def get_ceo_analytics(current_user: CurrentUser, session: SessionDep):
    """Analytics del CEO"""
    return {
        "message": "CEO Analytics - Coming soon",
        "user": current_user,
        "analytics": {
            "monthly_growth": 0,
            "user_acquisition": 0,
            "revenue_forecast": 0
        }
    } 