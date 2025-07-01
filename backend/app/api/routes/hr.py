from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/dashboard")
async def get_hr_dashboard(current_user: CurrentUser, session: SessionDep):
    """Dashboard de RRHH"""
    return {
        "message": "HR Dashboard",
        "user": current_user,
        "stats": {
            "total_employees": 0,
            "pending_evaluations": 0,
            "training_programs": 0
        }
    } 