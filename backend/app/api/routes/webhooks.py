"""Stripe webhook handler — keeps UserSubscriptionTable in sync."""

import logging
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.db import get_db
from sqlalchemy import update
from kila_models.models.base import SubscriptionStatus, SubscriptionTier
from kila_models.models.database import BrandPromptTable, UserSubscriptionTable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.stripe_secret_key


def _get_price_to_tier() -> dict[str, SubscriptionTier]:
    return {
        settings.stripe_pro_price_id: SubscriptionTier.pro,
    }


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events to update subscription state.

    Events handled:
    - checkout.session.completed → upgrade tier, save stripe IDs
    - customer.subscription.updated → tier/status changes
    - customer.subscription.deleted → cancel subscription
    - invoice.payment_failed → set status to past_due
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

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        # Look up by metadata.user_id (NOT stripe_customer_id — may not be stored yet)
        user_id = data_object.get("metadata", {}).get("user_id")
        if not user_id:
            logger.warning("checkout.session.completed missing metadata.user_id")
            return {"status": "ignored"}

        customer_id = data_object.get("customer")
        sub_id = data_object.get("subscription")
        price_id = None

        stripe_sub = None
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
            UserSubscriptionTable.user_id == user_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if not sub:
            logger.warning(f"No subscription found for user_id: {user_id}")
            return {"status": "not_found"}

        sub.tier = tier
        sub.status = SubscriptionStatus.active
        sub.trial_started_at = None
        sub.trial_expires_at = None
        sub.stripe_customer_id = customer_id
        sub.stripe_subscription_id = sub_id
        sub.cancel_at_period_end = False
        if stripe_sub and stripe_sub.get("current_period_end"):
            sub.current_period_end = datetime.fromtimestamp(
                stripe_sub["current_period_end"], tz=timezone.utc
            )
        await db.commit()
        logger.info(f"Upgraded subscription {sub.subscription_id} to {tier}")

    elif event_type == "customer.subscription.updated":
        user_id = data_object.get("metadata", {}).get("user_id")
        if not user_id:
            logger.warning("customer.subscription.updated missing metadata.user_id")
            return {"status": "ignored"}

        price_id = data_object["items"]["data"][0]["price"]["id"]
        tier = _get_price_to_tier().get(price_id)
        stripe_status = data_object.get("status")

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.user_id == user_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if not sub:
            logger.warning(f"No subscription found for user_id: {user_id}")
            return {"status": "not_found"}

        if tier:
            sub.tier = tier
        else:
            logger.warning(
                f"Unknown price_id in subscription.updated: {price_id}, skipping tier update"
            )

        if stripe_status == "past_due":
            sub.status = SubscriptionStatus.past_due
        elif stripe_status in ("canceled", "unpaid"):
            sub.status = SubscriptionStatus.cancelled
        elif stripe_status == "active":
            sub.status = SubscriptionStatus.active

        # Sync cancel_at_period_end and current_period_end
        sub.cancel_at_period_end = bool(data_object.get("cancel_at_period_end", False))
        period_end_ts = data_object.get("current_period_end")
        if period_end_ts:
            sub.current_period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc)

        await db.commit()
        logger.info(
            f"Updated subscription {sub.subscription_id}: tier={sub.tier}, status={sub.status}"
        )

    elif event_type == "customer.subscription.deleted":
        customer_id = data_object.get("customer")

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.stripe_customer_id == customer_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = SubscriptionStatus.cancelled
            sub.cancel_at_period_end = False

            # Deactivate all prompts for this user — offline scraper will skip them
            await db.execute(
                update(BrandPromptTable)
                .where(BrandPromptTable.user_id == sub.user_id)
                .values(is_active=False)
            )

            await db.commit()
            logger.info(
                f"Cancelled subscription {sub.subscription_id}; "
                f"deactivated all prompts for user {sub.user_id}"
            )

    elif event_type == "invoice.payment_failed":
        sub_id = data_object.get("subscription")
        if not sub_id:
            return {"status": "ignored"}

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.stripe_subscription_id == sub_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = SubscriptionStatus.past_due
            await db.commit()
            logger.info(f"Set subscription {sub.subscription_id} to past_due")

    return {"status": "ok"}
