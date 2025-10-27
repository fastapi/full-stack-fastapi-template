import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import AdministradorUser, CurrentUser, SessionDep
from app import crud
from app.models import (
    Alert,
    AlertPublic,
    AlertsPublic,
    AlertUpdate,
    AlertType,
    Message,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=AlertsPublic)
def read_alerts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    resolved: bool | None = None,
    product_id: uuid.UUID | None = None,
    alert_type: AlertType | None = None,
) -> Any:
    """
    Retrieve alerts.
    All authenticated users can view alerts.
    Filters: resolved (True/False/None for all), product_id, alert_type
    """
    count_statement = select(func.count()).select_from(Alert)
    statement = select(Alert)

    # Filter by resolved status
    if resolved is not None:
        count_statement = count_statement.where(Alert.is_resolved == resolved)
        statement = statement.where(Alert.is_resolved == resolved)

    # Filter by product
    if product_id:
        count_statement = count_statement.where(Alert.product_id == product_id)
        statement = statement.where(Alert.product_id == product_id)

    # Filter by alert type
    if alert_type:
        count_statement = count_statement.where(Alert.alert_type == alert_type)
        statement = statement.where(Alert.alert_type == alert_type)

    count = session.exec(count_statement).one()
    statement = statement.offset(skip).limit(limit).order_by(Alert.created_at.desc())
    alerts = session.exec(statement).all()

    return AlertsPublic(data=alerts, count=count)


@router.get("/active", response_model=AlertsPublic)
def read_active_alerts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve only active (unresolved) alerts.
    Useful for dashboard/monitoring.
    """
    count_statement = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.is_resolved == False)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Alert)
        .where(Alert.is_resolved == False)
        .offset(skip)
        .limit(limit)
        .order_by(Alert.created_at.desc())
    )
    alerts = session.exec(statement).all()

    return AlertsPublic(data=alerts, count=count)


@router.get("/{id}", response_model=AlertPublic)
def read_alert(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get alert by ID.
    All authenticated users can view alerts.
    """
    alert = crud.get_alert_by_id(session=session, alert_id=id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{id}/resolve", response_model=AlertPublic)
def resolve_alert(
    *,
    session: SessionDep,
    current_user: AdministradorUser,
    id: uuid.UUID,
    alert_update: AlertUpdate,
) -> Any:
    """
    Resolve an alert manually.
    Only administrador can resolve alerts.
    Note: Alerts are also auto-resolved when stock is replenished.
    """
    db_alert = crud.get_alert_by_id(session=session, alert_id=id)
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if db_alert.is_resolved:
        raise HTTPException(status_code=400, detail="Alert is already resolved")

    alert = crud.resolve_alert(
        session=session,
        db_alert=db_alert,
        resolved_by=current_user.id,
        notes=alert_update.notes
    )
    return alert


@router.get("/product/{product_id}", response_model=AlertsPublic)
def read_alerts_by_product(
    session: SessionDep,
    current_user: CurrentUser,
    product_id: uuid.UUID,
    resolved: bool | None = None,
) -> Any:
    """
    Get all alerts for a specific product.
    Filter by resolved status (optional).
    """
    statement = select(Alert).where(Alert.product_id == product_id)
    count_statement = select(func.count()).select_from(Alert).where(Alert.product_id == product_id)

    if resolved is not None:
        statement = statement.where(Alert.is_resolved == resolved)
        count_statement = count_statement.where(Alert.is_resolved == resolved)

    statement = statement.order_by(Alert.created_at.desc())
    alerts = session.exec(statement).all()
    count = session.exec(count_statement).one()

    return AlertsPublic(data=alerts, count=count)
