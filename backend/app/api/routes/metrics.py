from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_manager_or_admin
from app.models import Item, MetricsPublic, User

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(get_current_manager_or_admin)],
)


@router.get("/", response_model=MetricsPublic)
def read_metrics(session: SessionDep) -> MetricsPublic:
    user_count = session.exec(select(func.count()).select_from(User)).one()
    item_count = session.exec(select(func.count()).select_from(Item)).one()
    return MetricsPublic(user_count=user_count, item_count=item_count)
