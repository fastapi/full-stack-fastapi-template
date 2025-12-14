"""
Stripe payment API routes.

Handles checkout session creation and webhook processing for premium
user upgrades. The checkout flow redirects users to Stripe's hosted
payment page, and webhooks handle fulfillment after successful payment.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.premium_users.models import PremiumUser, utc_now
from app.premium_users.stripe import get_stripe_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stripe", tags=["stripe"])


class CheckoutSessionResponse(BaseModel):
    """Response containing Stripe Checkout URL."""

    checkout_url: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    session: SessionDep,
    current_user: CurrentUser,
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout Session for premium upgrade.

    Returns a URL to redirect the user to Stripe's hosted checkout page.
    After payment, Stripe redirects back to our success URL and sends
    a webhook to fulfill the order.
    """
    logger.debug(f"Creating checkout session for user {current_user.id}")

    # Check if user is already premium
    existing = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == current_user.id)
    ).first()

    if existing and existing.is_premium:
        logger.debug(f"User {current_user.id} is already premium")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already premium",
        )

    stripe = get_stripe_client()

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Premium Upgrade",
                            "description": "Unlock unlimited items and premium badge",
                        },
                        "unit_amount": settings.STRIPE_PREMIUM_PRICE_CENTS,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{settings.FRONTEND_HOST}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_HOST}/settings",
            metadata={
                "user_id": str(current_user.id),
            },
        )

        logger.debug(f"Created checkout session {checkout_session.id} for user {current_user.id}")

        return CheckoutSessionResponse(checkout_url=checkout_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, session: SessionDep) -> dict:
    """
    Handle Stripe webhook events.

    Stripe sends events here when payment status changes. We use this
    to fulfill the premium upgrade after successful payment.

    Note: This endpoint is PUBLIC (no auth) - Stripe calls it directly.
    Security comes from signature verification.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    stripe = get_stripe_client()

    try:
        event = stripe.webhooks.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.debug(f"Received Stripe webhook: {event['type']}")

    # Handle checkout session completed
    if event["type"] == "checkout.session.completed":
        checkout_session = event["data"]["object"]
        _handle_checkout_completed(session, checkout_session)

    return {"status": "success"}


def _handle_checkout_completed(
    session: Session,
    checkout_session: dict,
) -> None:
    """
    Process successful checkout - grant premium status to user.

    Creates or updates PremiumUser record with payment details.
    Idempotent: safe to call multiple times for same checkout session.
    """
    user_id_str = checkout_session.get("metadata", {}).get("user_id")
    if not user_id_str:
        logger.error("No user_id in checkout session metadata")
        return

    user_id = UUID(user_id_str)
    stripe_customer_id = checkout_session.get("customer")
    payment_intent_id = checkout_session.get("payment_intent")

    logger.debug(f"Processing premium upgrade for user {user_id}")

    # Check for existing record (idempotency)
    existing = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == user_id)
    ).first()

    if existing:
        if existing.is_premium:
            logger.debug(f"User {user_id} already premium, skipping")
            return

        # Update existing record
        existing.is_premium = True
        existing.stripe_customer_id = stripe_customer_id
        existing.payment_intent_id = payment_intent_id
        existing.paid_at = utc_now()
        existing.updated_at = utc_now()
        session.add(existing)
    else:
        # Create new record
        premium_user = PremiumUser(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            is_premium=True,
            payment_intent_id=payment_intent_id,
            paid_at=utc_now(),
        )
        session.add(premium_user)

    session.commit()
    logger.debug(f"User {user_id} upgraded to premium")
