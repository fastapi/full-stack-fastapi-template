# STRIPE-1.4: Stripe Webhook Handler

## Status: COMPLETE

## Summary
Create a webhook endpoint that receives events from Stripe. When a checkout session completes successfully, create/update the PremiumUser record to grant premium status.

## Acceptance Criteria
- [x] POST `/api/v1/stripe/webhook` endpoint exists
- [x] Endpoint verifies Stripe webhook signature
- [x] Handles `checkout.session.completed` event
- [x] Creates PremiumUser record with is_premium=True
- [x] Extracts user_id from session metadata
- [x] Stores stripe_customer_id and payment_intent_id
- [x] Handles duplicate webhooks idempotently
- [x] Returns 200 to acknowledge receipt
- [x] Logs all webhook events for debugging

## Technical Details

### Webhook Endpoint
Add to `backend/app/api/routes/stripe.py`:
```python
from fastapi import Request
from datetime import datetime


@router.post("/webhook")
async def stripe_webhook(request: Request, session: SessionDep) -> dict:
    """
    Handle Stripe webhook events.

    Stripe sends events here when payment status changes.
    We use this to fulfill the premium upgrade after successful payment.

    Note: This endpoint must NOT require authentication - Stripe calls it directly.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    stripe = get_stripe_client()

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info(f"Received Stripe webhook: {event['type']}")

    # Handle checkout session completed
    if event["type"] == "checkout.session.completed":
        checkout_session = event["data"]["object"]
        await handle_checkout_completed(session, checkout_session)

    return {"status": "success"}


async def handle_checkout_completed(
    session: Session,
    checkout_session: dict,
) -> None:
    """
    Process successful checkout - grant premium status to user.

    Creates or updates PremiumUser record with payment details.
    Idempotent: safe to call multiple times for same session.
    """
    from uuid import UUID

    user_id_str = checkout_session.get("metadata", {}).get("user_id")
    if not user_id_str:
        logger.error("No user_id in checkout session metadata")
        return

    # Convert string back to UUID (stored as string in Stripe metadata)
    user_id = UUID(user_id_str)
    stripe_customer_id = checkout_session.get("customer")
    payment_intent_id = checkout_session.get("payment_intent")

    logger.info(f"Processing premium upgrade for user {user_id}")

    # Check for existing record (idempotency)
    existing = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == user_id)
    ).first()

    if existing:
        # Update existing record
        if existing.is_premium:
            logger.info(f"User {user_id} already premium, skipping")
            return

        existing.is_premium = True
        existing.stripe_customer_id = stripe_customer_id
        existing.payment_intent_id = payment_intent_id
        existing.paid_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()
        session.add(existing)
    else:
        # Create new record
        premium_user = PremiumUser(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            is_premium=True,
            payment_intent_id=payment_intent_id,
            paid_at=datetime.utcnow(),
        )
        session.add(premium_user)

    session.commit()
    logger.info(f"User {user_id} upgraded to premium")
```

### Testing with Stripe CLI
```bash
# Install Stripe CLI
# macOS: brew install stripe/stripe-cli/stripe
# Linux: see https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook

# Copy the webhook signing secret (whsec_xxx) to .env

# In another terminal, trigger test event
stripe trigger checkout.session.completed
```

### Webhook Security
1. **Signature Verification**: Always verify webhook signature
2. **HTTPS**: Production webhook endpoint must use HTTPS
3. **Idempotency**: Handle duplicate events gracefully
4. **Acknowledge quickly**: Return 200 within 30 seconds

### Files to Modify
1. `backend/app/api/routes/stripe.py` - Add webhook endpoint

## Webhook Event Payload
Example `checkout.session.completed` event:
```json
{
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_xxxxx",
      "customer": "cus_xxxxx",
      "payment_intent": "pi_xxxxx",
      "payment_status": "paid",
      "metadata": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  }
}
```
**Note:** `user_id` is stored as a UUID string in Stripe metadata and converted back to UUID in webhook handler.

## Dependencies
- STRIPE-1.1 (PremiumUser model)
- STRIPE-1.2 (Stripe configuration)
- STRIPE-1.3 (Checkout session creates the metadata)

## Testing
- [ ] Valid webhook with correct signature returns 200
- [ ] Invalid signature returns 400
- [ ] Missing signature returns 400
- [ ] checkout.session.completed creates PremiumUser
- [ ] Duplicate webhook doesn't create duplicate record
- [ ] User ID extracted from metadata correctly
- [ ] stripe_customer_id stored correctly
- [ ] payment_intent_id stored correctly
- [ ] paid_at timestamp set correctly

## Local Development Setup
1. Install Stripe CLI
2. Run `stripe login`
3. Run `stripe listen --forward-to localhost:8000/api/v1/stripe/webhook`
4. Copy webhook secret to `.env`
5. Run `stripe trigger checkout.session.completed` to test

## Production Setup
1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://yourdomain.com/api/v1/stripe/webhook`
3. Select events: `checkout.session.completed`
4. Copy signing secret to production environment

## Notes
- Webhook endpoint is PUBLIC (no auth) - Stripe calls it
- Security comes from signature verification
- Always return 200 quickly, do heavy processing async if needed
- Stripe retries failed webhooks for up to 3 days
