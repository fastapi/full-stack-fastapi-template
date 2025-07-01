from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/manager", tags=["manager"])


@router.get("/dashboard")
async def get_manager_dashboard(current_user: CurrentUser, session: SessionDep):
    """Dashboard del Manager"""
    return {
        "message": "Manager Dashboard",
        "user": current_user,
        "stats": {
            "branch_performance": 0,
            "team_size": 0,
            "monthly_revenue": 0
        }
    }


@router.get("/team")
async def get_manager_team(current_user: CurrentUser, session: SessionDep):
    """Equipo del Manager"""
    return {
        "message": "Manager Team - Coming soon",
        "user": current_user,
        "team": []
    } 