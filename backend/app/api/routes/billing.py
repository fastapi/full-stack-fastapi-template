"""Stripe billing endpoints: Checkout Session + Customer Portal."""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.db import get_db
from kila_models.models.base import SubscriptionStatus, SubscriptionTier
from kila_models.models.database import UserSubscriptionTable, UsersTable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

stripe.api_key = settings.stripe_secret_key


class CheckoutRequest(BaseModel):
    price_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """Create a Stripe Checkout session for subscription upgrade."""
    valid_prices = {settings.stripe_basic_price_id, settings.stripe_pro_price_id}
    if body.price_id not in valid_prices:
        raise HTTPException(status_code=400, detail="Invalid price ID")

    stmt = select(UserSubscriptionTable).where(
        UserSubscriptionTable.user_id == current_user.user_id
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")

    if (
        sub.status == SubscriptionStatus.active
        and sub.tier != SubscriptionTier.free_trial
    ):
        raise HTTPException(
            status_code=400, detail="Already have an active paid subscription"
        )

    checkout_params: dict = {
        "mode": "subscription",
        "line_items": [{"price": body.price_id, "quantity": 1}],
        "success_url": f"{settings.stripe_frontend_url}/app/billing?status=success",
        "cancel_url": f"{settings.stripe_frontend_url}/app/pricing?status=cancelled",
        "metadata": {"user_id": current_user.user_id},
        "subscription_data": {"metadata": {"user_id": current_user.user_id}},
    }

    if sub.stripe_customer_id:
        checkout_params["customer"] = sub.stripe_customer_id
    else:
        checkout_params["customer_email"] = current_user.email

    session = stripe.checkout.Session.create(**checkout_params)
    return CheckoutResponse(checkout_url=session.url)


@router.post("/create-portal-session", response_model=PortalResponse)
async def create_portal_session(
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """Create a Stripe Customer Portal session for subscription management."""
    stmt = select(UserSubscriptionTable).where(
        UserSubscriptionTable.user_id == current_user.user_id
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if not sub or not sub.stripe_customer_id:
        raise HTTPException(
            status_code=400, detail="No Stripe customer found. Please subscribe first."
        )

    portal_session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{settings.stripe_frontend_url}/app/billing",
    )
    return PortalResponse(portal_url=portal_session.url)
