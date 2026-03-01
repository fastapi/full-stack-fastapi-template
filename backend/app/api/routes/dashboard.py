from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.models import RecentTemplatesPublic
from app.services import generation_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/recent-templates", response_model=RecentTemplatesPublic)
def read_recent_templates(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(default=5, ge=1, le=20),
) -> Any:
    return generation_service.get_recent_templates_for_dashboard(
        session=session,
        current_user=current_user,
        limit=limit,
    )
