# STRIPE-1.3: Checkout Session Endpoint

## Status: COMPLETE

## Summary
Create an API endpoint that generates a Stripe Checkout Session for the $1 premium upgrade. Returns a URL that the frontend redirects to.

## Acceptance Criteria
- [x] POST `/api/v1/stripe/create-checkout-session` endpoint exists
- [x] Endpoint requires authentication (logged-in user)
- [x] Creates Stripe Checkout Session with correct price ($1.00)
- [x] Stores user_id in session metadata for webhook
- [x] Returns checkout URL to frontend
- [x] Handles errors gracefully (Stripe API failures)
- [x] Prevents already-premium users from purchasing again

## Technical Details

### API Route
Create `backend/app/api/routes/stripe.py`:
```python
"""
Stripe payment API routes.

Handles checkout session creation and webhook processing
for premium user upgrades.
"""
import logging

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.stripe import get_stripe_client
from app.models import PremiumUser

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
    After payment, Stripe redirects back to our success URL.
    """
    # Check if user is already premium
    existing = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == current_user.id)
    ).first()

    if existing and existing.is_premium:
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
                "user_id": str(current_user.id),  # UUID converted to string for Stripe metadata
            },
        )

        logger.info(f"Created checkout session for user {current_user.id}")

        return CheckoutSessionResponse(checkout_url=checkout_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )
```

### Register Router
Modify `backend/app/api/main.py`:
```python
from app.api.routes import stripe

api_router.include_router(stripe.router)
```

### Update Config for Frontend Host
Ensure `backend/app/core/config.py` has:
```python
FRONTEND_HOST: str = "http://localhost:5173"  # Or from env
```

### Files to Create/Modify
1. `backend/app/api/routes/stripe.py` - Create new file
2. `backend/app/api/main.py` - Register stripe router
3. `backend/app/core/config.py` - Add FRONTEND_HOST if missing

## API Contract

### Request
```
POST /api/v1/stripe/create-checkout-session
Authorization: Bearer <token>
```

### Success Response (200)
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_xxxxx"
}
```

### Error Responses
- 400: User already premium
- 401: Not authenticated
- 500: Stripe API error

## Dependencies
- STRIPE-1.1 (PremiumUser model)
- STRIPE-1.2 (Stripe configuration)

## Testing
- [ ] Endpoint requires authentication
- [ ] Returns valid Stripe checkout URL
- [ ] URL opens Stripe checkout page
- [ ] User ID is in session metadata
- [ ] Already premium user gets 400 error
- [ ] Invalid Stripe key returns 500 error

## Notes
- Frontend will redirect to `checkout_url`, not open iframe
- `{CHECKOUT_SESSION_ID}` is a Stripe placeholder, replaced automatically
- Success URL includes session_id for verification on frontend
- Cancel URL returns user to settings page
