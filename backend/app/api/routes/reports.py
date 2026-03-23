from datetime import date, datetime as dt, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.storage.report_storage import get_report_storage
from kila_models.models import (
    WeeklyReportSnapshotTable,
    WeeklyReportSubscriptionTable,
    BrandUserTable,
)

router = APIRouter()


def _last_completed_week_start() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday() + 7)


async def _check_brand_access(db: AsyncSession, user_id: str, brand_id: str):
    result = await db.execute(
        select(BrandUserTable).where(
            and_(
                BrandUserTable.brand_id == brand_id,
                BrandUserTable.user_id == user_id,
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this brand")


async def get_snapshot(db: AsyncSession, brand_id: str, week_start: date):
    result = await db.execute(
        select(WeeklyReportSnapshotTable).where(
            and_(
                WeeklyReportSnapshotTable.brand_id == brand_id,
                WeeklyReportSnapshotTable.week_start == week_start,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_subscription(db: AsyncSession, user_id: str, brand_id: str):
    result = await db.execute(
        select(WeeklyReportSubscriptionTable).where(
            and_(
                WeeklyReportSubscriptionTable.user_id == user_id,
                WeeklyReportSubscriptionTable.brand_id == brand_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def upsert_subscription(db: AsyncSession, user_id: str, brand_id: str, is_active: bool):
    now = dt.utcnow()
    stmt = pg_insert(WeeklyReportSubscriptionTable).values(
        user_id=user_id,
        brand_id=brand_id,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    ).on_conflict_do_update(
        constraint="uq_subscription_user_brand",
        set_={"is_active": is_active, "updated_at": now},
    )
    await db.execute(stmt)
    await db.commit()


@router.get("/reports/weekly/{brand_id}")
async def download_weekly_report(
    brand_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the pre-generated PDF for the most recently completed week."""
    await _check_brand_access(db, current_user.user_id, brand_id)

    week_start = _last_completed_week_start()
    snapshot = await get_snapshot(db, brand_id, week_start)

    if not snapshot or not snapshot.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not yet available — check back after Monday",
        )

    from app.config import settings as app_settings
    storage = get_report_storage(
        backend=app_settings.report_storage_backend,
        path=app_settings.report_storage_path,
    )
    try:
        pdf_bytes = storage.get(snapshot.pdf_path)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")

    brand_name = snapshot.snapshot_data.get("brand_name", brand_id)
    filename = f"kila-report-{brand_name}-{week_start}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class SubscriptionRequest(BaseModel):
    is_active: bool


class SubscriptionResponse(BaseModel):
    is_active: bool


@router.get("/brands/{brand_id}/reports/weekly/subscription", response_model=SubscriptionResponse)
async def get_report_subscription(
    brand_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await get_subscription(db, current_user.user_id, brand_id)
    return SubscriptionResponse(is_active=sub.is_active if sub else False)


@router.post("/brands/{brand_id}/reports/weekly/subscription", response_model=SubscriptionResponse)
async def set_report_subscription(
    brand_id: str,
    body: SubscriptionRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await upsert_subscription(db, current_user.user_id, brand_id, body.is_active)
    return SubscriptionResponse(is_active=body.is_active)
