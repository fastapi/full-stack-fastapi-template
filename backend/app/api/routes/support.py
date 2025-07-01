from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/dashboard")
async def get_support_dashboard(current_user: CurrentUser, session: SessionDep):
    """Dashboard de Soporte"""
    return {
        "message": "Support Dashboard",
        "user": current_user,
        "stats": {
            "open_tickets": 0,
            "resolved_today": 0,
            "customer_satisfaction": 0
        }
    } 