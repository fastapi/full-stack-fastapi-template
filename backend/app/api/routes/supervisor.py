from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/supervisor", tags=["supervisor"])


@router.get("/dashboard")
async def get_supervisor_dashboard(current_user: CurrentUser, session: SessionDep):
    """Dashboard del Supervisor"""
    return {
        "message": "Supervisor Dashboard",
        "user": current_user,
        "stats": {
            "team_agents": 0,
            "pending_operations": 0,
            "team_performance": 0
        }
    }
