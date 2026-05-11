from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, require_roles
from app.models import Item, User, UserRole

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/", dependencies=[Depends(require_roles(UserRole.admin, UserRole.manager))]
)
def read_metrics(session: SessionDep) -> dict[str, Any]:
    """
    Return simple operational metrics for privileged users.
    """
    user_count = session.exec(select(func.count()).select_from(User)).one()
    item_count = session.exec(select(func.count()).select_from(Item)).one()
    return {
        "users": user_count,
        "items": item_count,
        "summary": "Demo insights visible to admins and managers.",
    }
