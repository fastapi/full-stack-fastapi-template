import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.websocket import manager
from app.models import (
    Message,
    Notification,
    NotificationCreate,
    NotificationPublic,
    NotificationsPublic,
    NotificationUpdate,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationsPublic)
def read_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> Any:
    """
    Retrieve notifications for the current user.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Notification)
        if unread_only:
            count_statement = count_statement.where(Notification.is_read == False)
        count = session.exec(count_statement).one()

        unread_count_statement = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.is_read == False)
        )
        unread_count = session.exec(unread_count_statement).one()

        statement = (
            select(Notification)
            .order_by(col(Notification.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        if unread_only:
            statement = statement.where(Notification.is_read == False)
        notifications = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == current_user.id)
        )
        if unread_only:
            count_statement = count_statement.where(Notification.is_read == False)
        count = session.exec(count_statement).one()

        unread_count_statement = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == current_user.id)
            .where(Notification.is_read == False)
        )
        unread_count = session.exec(unread_count_statement).one()

        statement = (
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(col(Notification.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        if unread_only:
            statement = statement.where(Notification.is_read == False)
        notifications = session.exec(statement).all()

    notifications_public = [
        NotificationPublic.model_validate(notification)
        for notification in notifications
    ]
    return NotificationsPublic(
        data=notifications_public, count=count, unread_count=unread_count
    )


@router.get("/{id}", response_model=NotificationPublic)
def read_notification(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get notification by ID.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not current_user.is_superuser and (notification.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return notification


@router.post("/", response_model=NotificationPublic)
async def create_notification(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    notification_in: NotificationCreate,
) -> Any:
    """
    Create new notification.
    Only superusers can create notifications for other users.
    Regular users can only create notifications for themselves.
    """
    if not current_user.is_superuser and notification_in.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create notifications for other users",
        )

    notification = Notification.model_validate(notification_in)
    session.add(notification)
    session.commit()
    session.refresh(notification)

    notification_public = NotificationPublic.model_validate(notification)
    await manager.send_notification(notification_public, notification.user_id)

    return notification


@router.put("/{id}", response_model=NotificationPublic)
def update_notification(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    notification_in: NotificationUpdate,
) -> Any:
    """
    Update a notification.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not current_user.is_superuser and (notification.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = notification_in.model_dump(exclude_unset=True)
    notification.sqlmodel_update(update_dict)
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.delete("/{id}")
def delete_notification(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a notification.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not current_user.is_superuser and (notification.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(notification)
    session.commit()
    return Message(message="Notification deleted successfully")


@router.post("/{id}/mark-read", response_model=NotificationPublic)
def mark_notification_read(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Mark a notification as read.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not current_user.is_superuser and (notification.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.post("/mark-all-read", response_model=Message)
def mark_all_notifications_read(
    session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Mark all notifications as read for the current user.
    """
    statement = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    )
    notifications = session.exec(statement).all()

    for notification in notifications:
        notification.is_read = True
        session.add(notification)

    session.commit()
    return Message(message=f"Marked {len(notifications)} notifications as read")
