import logging
import stripe
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.config import settings
from kila_models.models.database import UserSubscriptionTable
from kila_models.models.base import SubscriptionTier, SubscriptionStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _get_price_to_tier() -> dict[str, SubscriptionTier]:
    return {
        settings.stripe_basic_price_id: SubscriptionTier.basic,
        settings.stripe_pro_price_id: SubscriptionTier.pro,
    }


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events to update subscription tiers.

    Events handled:
    - checkout.session.completed → upgrade tier to basic or pro
    - customer.subscription.deleted → cancel subscription
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.errors.SignatureVerificationError:
        logger.warning("Invalid Stripe webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Stripe webhook parse error: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        price_id = None

        # Try to get price_id from subscription line items
        sub_id = session.get("subscription")
        if sub_id:
            try:
                stripe_sub = stripe.Subscription.retrieve(sub_id)
                price_id = stripe_sub["items"]["data"][0]["price"]["id"]
            except Exception as e:
                logger.error(f"Failed to retrieve Stripe subscription: {e}")

        tier = _get_price_to_tier().get(price_id)
        if not tier:
            logger.warning(f"Unknown price_id in checkout: {price_id}")
            return {"status": "ignored"}

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.stripe_customer_id == customer_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if not sub:
            logger.warning(f"No subscription found for Stripe customer: {customer_id}")
            return {"status": "not_found"}

        sub.tier = tier
        sub.status = SubscriptionStatus.active
        sub.trial_started_at = None
        sub.trial_expires_at = None
        sub.stripe_subscription_id = sub_id
        await db.commit()
        logger.info(f"Upgraded subscription {sub.subscription_id} to {tier}")

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.stripe_customer_id == customer_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = SubscriptionStatus.cancelled
            await db.commit()
            logger.info(f"Cancelled subscription {sub.subscription_id}")

    return {"status": "ok"}
