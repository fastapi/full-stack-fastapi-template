"""
Premium User database model.

Stores Stripe payment and premium status data with a one-to-one
relationship to the User table. Created when a user completes
Stripe checkout and used to check premium status for feature gating.
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class PremiumUser(SQLModel, table=True):
    """
    Stores Stripe payment and premium status data.
    One-to-one relationship with User.

    Created when a user completes Stripe checkout.
    Used to check premium status for feature gating (e.g., item limits).
    """

    __tablename__ = "premium_user"

    premium_user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
    stripe_customer_id: str = Field(index=True)  # Stripe's customer ID (cus_xxx)
    is_premium: bool = Field(default=False)  # Premium status flag
    payment_intent_id: str | None = Field(default=None)  # Stripe payment intent (pi_xxx)
    paid_at: datetime | None = Field(default=None)  # When payment completed
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
