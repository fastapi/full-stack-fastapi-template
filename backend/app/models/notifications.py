# app/models/notifications.py

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, String


class PushToken(SQLModel, table=True):
    """
    Stores each user’s Expo push token.
    """
    __tablename__ = "push_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, unique=True, index=True
    )
    expo_token: str = Field(
        sa_column=Column("expo_token", String, unique=True, index=True),
        description="The Expo Push Token (e.g. ExponentPushToken[…])",
    )


class CustomReminderBase(SQLModel):
    """
    Shared properties for a scheduled reminder.
    """
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, index=True, description="Which user"
    )
    expo_token: str = Field(description="Store the Expo push token here")
    remind_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        description="UTC timestamp when this reminder should fire",
    )
    message: str = Field(max_length=255, description="Your reminder text")


class CustomReminder(CustomReminderBase, table=True):
    """
    A one-off reminder. Once sent, we’ll set sent_at so it isn’t sent again.
    """
    __tablename__ = "custom_reminders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Set to now() after sending",
    )
