# Metrics API routes with role-based access for admin and manager roles.
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, require_permission
from app.core.permissions import Permission
from app.models import Message

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/",
    dependencies=[Depends(require_permission(Permission.METRICS_VIEW))],
    response_model=Message,
)
def read_metrics(_current_user: CurrentUser) -> Any:
    return Message(
        message="Metrics stub: total users=42, active sessions=7, conversion rate=3.2%"
    )
