from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.crudFuncs import (
    create_or_update_push_token,
    schedule_custom_reminder
)
from app.core.db import get_session    # adjust if your DB‐session dependency lives elsewhere
from app.models import User

router = APIRouter(tags=["notifications"])


# Pydantic schema that the client will POST when registering a token
class PushTokenPayload(BaseModel):
    user_id: uuid.UUID
    expo_token: str


@router.post("/register_push_token", status_code=201)
def register_push_token(
    payload: PushTokenPayload,
    session: Session = Depends(get_session),
):
    """
    Client calls this with { user_id, expo_token } to store/update the Expo token.
    """
    try:
        token_obj = create_or_update_push_token(
            session=session,
            user_id=payload.user_id,
            expo_token=payload.expo_token,
        )
        return {"status": "ok", "push_token_id": token_obj.id}
    except ValueError as e:
        # If user_id doesn’t exist in Users table
        raise HTTPException(status_code=404, detail=str(e))


# Pydantic schema that the client will POST when scheduling a reminder
class CustomReminderPayload(BaseModel):
    user_id: uuid.UUID
    expo_token: str
    remind_time: datetime       # e.g. "2025-06-05T12:00:00Z"
    message: str


@router.post("/schedule_reminder", status_code=201)
def schedule_reminder_endpoint(
    payload: CustomReminderPayload,
    session: Session = Depends(get_session),
):
    """
    Client calls this with { user_id, expo_token, remind_time, message }
    to schedule a one‐off reminder.
    """
    try:
        rem_obj = schedule_custom_reminder(
            session=session,
            user_id=payload.user_id,
            expo_token=payload.expo_token,
            remind_time=payload.remind_time,
            message=payload.message,
        )
        return {"status": "scheduled", "reminder_id": rem_obj.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
