from fastapi import APIRouter
from sqlmodel import col, func, select

from app.api.deps import SessionDep, StaffUser
from app.models import Item, MetricsPublic, User

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", response_model=MetricsPublic)
def read_metrics(session: SessionDep, _: StaffUser) -> MetricsPublic:
    """
    Retrieve user and item counts.
    """
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(col(User.is_active))
    ).one()
    total_items = session.exec(select(func.count()).select_from(Item)).one()
    return MetricsPublic(
        total_users=total_users, active_users=active_users, total_items=total_items
    )
