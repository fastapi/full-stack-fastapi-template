from datetime import datetime, timezone, timedelta

from nanoid import generate
from sqlalchemy.ext.asyncio import AsyncSession

from kila_models.models.database import UserSubscriptionTable
from kila_models.models.base import SubscriptionTier, SubscriptionStatus


async def create_free_trial_subscription(user_id: str, db: AsyncSession) -> None:
    """Create a free_trial subscription row for a newly created user. Does not commit."""
    now = datetime.now(timezone.utc)
    subscription = UserSubscriptionTable(
        subscription_id=f"S_{generate(size=10)}",
        user_id=user_id,
        company_id=None,
        tier=SubscriptionTier.free_trial,
        status=SubscriptionStatus.active,
        trial_started_at=now,
        trial_expires_at=now + timedelta(days=28),
    )
    db.add(subscription)
