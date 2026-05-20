from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, require_role
from app.models import Item, MetricsPublic, User, UserRole

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/",
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))],
    response_model=MetricsPublic,
)
def read_metrics(session: SessionDep) -> MetricsPublic:
    """
    Return basic app metrics. Accessible by admins and managers.
    """
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
    ).one()
    total_items = session.exec(select(func.count()).select_from(Item)).one()

    return MetricsPublic(
        total_users=total_users,
        active_users=active_users,
        total_items=total_items,
    )
