from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, require_permission
from app.core import rbac
from app.models import Item, MetricsPublic, User

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(require_permission(rbac.PERMISSION_METRICS_VIEW))],
)


@router.get("/")
def read_metrics(session: SessionDep) -> MetricsPublic:
    """
    Basic usage metrics. A stub — not a real analytics pipeline.
    """
    user_count = session.exec(select(func.count()).select_from(User)).one()
    item_count = session.exec(select(func.count()).select_from(Item)).one()
    return MetricsPublic(user_count=user_count, item_count=item_count)
