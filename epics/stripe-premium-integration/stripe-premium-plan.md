# Stripe Premium Integration - A Seashell Company

## Epic Details
- **Epic ID**: stripe-premium-integration
- **Status**: Planning
- **Target**: One-time $1 payment for Premium tier with feature gating
- **Approach**: Stripe Checkout (hosted) with webhook-based fulfillment

## Goal
Add a simple premium tier payment system that demonstrates Stripe integration patterns. Free users are limited to 2 items, premium users (one-time $1 payment) get unlimited items and a star badge next to their name.

## Requirements
- **Payment Type**: One-time payment ($1.00 USD)
- **Premium Features**:
  - Unlimited items (free tier limited to 2)
  - Star ⭐ badge next to username
- **Payment Method**: Stripe Checkout (hosted page)
- **Upgrade Locations**: Settings page + Items page
- **User Management**: View premium status, no cancellation needed (one-time)

## High-Level Implementation Phases

### Phase 1: Database and Backend Setup
**Ticket STRIPE-1.1: Create PremiumUser Model and Migration**
- Create new `PremiumUser` model in `backend/app/models.py`
- Add fields: premium_user_id (PK), user_id (FK), stripe_customer_id, is_premium, payment_intent_id, paid_at, timestamps
- Create Alembic migration for new table
- Test migration locally (up and down)

**Ticket STRIPE-1.2: Stripe API Configuration**
- Add Stripe secret key to backend .env
- Install stripe Python package
- Create Stripe utility module (backend/app/core/stripe.py)
- Initialize Stripe client
- Add Stripe webhook secret to .env

**Ticket STRIPE-1.3: Checkout Session Endpoint**
- Create `/api/stripe/create-checkout-session` POST endpoint
- Authenticate user (require login)
- Create Stripe Checkout Session ($1 one-time payment)
- Set success/cancel URLs
- Store user_id in session metadata
- Return session URL to frontend

**Ticket STRIPE-1.4: Stripe Webhook Handler**
- Create `/api/stripe/webhook` POST endpoint
- Verify webhook signature
- Handle `checkout.session.completed` event
- Extract user_id from session metadata
- Create/update PremiumUser record with:
  - stripe_customer_id, is_premium=True, payment_intent_id, paid_at=now
- Log payment success
- Handle webhook idempotency (check if already processed)

### Phase 2: Item Limit Enforcement
**Ticket STRIPE-2.1: Add Item Count Check**
- Update `POST /api/items` endpoint
- Query PremiumUser table for user's premium status (LEFT JOIN)
- If no record or is_premium=False, count user's existing items
- Return 403 if count >= 2 with clear error message
- Allow creation if premium or count < 2

**Ticket STRIPE-2.2: Frontend Error Handling**
- Update items creation to handle 403 error
- Show upgrade modal when limit reached
- Include upgrade button in modal
- Test error flow

### Phase 3: Frontend Premium UI
**Ticket STRIPE-3.1: Premium Badge Component**
- Create `<PremiumBadge />` component (star icon)
- Add to navbar next to username
- Add to settings My Profile section
- Style consistently across app

**Ticket STRIPE-3.2: Settings Page Premium Section**
- Update Settings/My Profile to show premium status
- Show "Premium Member ⭐" if premium
- Show "Free Tier" with upgrade button if not premium
- Add Stripe Checkout integration button
- Handle redirect to Stripe Checkout

**Ticket STRIPE-3.3: Items Page Upgrade CTA**
- Add item count display "X/2 items (Free)" or "X items (Premium)"
- Show upgrade button when approaching/at limit
- Position near "Add Item" button
- Use same Stripe Checkout flow

**Ticket STRIPE-3.4: Payment Success Page**
- Create `/payment-success` route
- Show success message after Stripe redirect
- Refresh user data to show premium badge
- Redirect to dashboard after 3 seconds

### Phase 4: Testing and Polish
**Ticket STRIPE-4.1: End-to-End Payment Testing**
- Test full payment flow with Stripe test mode
- Test webhook delivery locally (Stripe CLI)
- Verify premium status updates correctly
- Test item limit enforcement before/after upgrade
- Test edge cases (duplicate webhooks, failed payments)

**Ticket STRIPE-4.2: Error Handling and UX Polish**
- Handle Stripe Checkout errors gracefully
- Add loading states during checkout creation
- Handle webhook failures (retry logic)
- Add user-friendly error messages
- Test network failures

**Ticket STRIPE-4.3: Production Deployment Prep**
- Document Stripe webhook endpoint URL
- Add Stripe webhook to production config
- Test with Stripe production mode
- Update environment variables documentation
- Create deployment checklist

## Success Criteria
- [ ] Free users can create up to 2 items
- [ ] Free users blocked from creating 3rd item
- [ ] Upgrade button visible in Settings and Items page
- [ ] Stripe Checkout opens and processes $1 payment
- [ ] Webhook updates user to premium successfully
- [ ] Premium badge appears next to username
- [ ] Premium users can create unlimited items
- [ ] Payment success page shows after checkout
- [ ] Handles Stripe test cards correctly
- [ ] Webhook signature verification works
- [ ] Idempotent webhook handling (no duplicate credits)

## Technical Stack
- **Backend**: FastAPI, SQLModel, Stripe Python SDK
- **Database**: PostgreSQL (new PremiumUser table)
- **Frontend**: React, TanStack Router, Stripe Checkout
- **Payment**: Stripe Checkout (hosted)
- **Webhooks**: Stripe webhooks for fulfillment

## Data Model Changes
```python
# New PremiumUser table
class PremiumUser(SQLModel, table=True):
    """
    Stores Stripe payment and premium status data.
    One-to-one relationship with User.
    """
    premium_user_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    stripe_customer_id: str  # Stripe's customer ID
    is_premium: bool = False  # Premium status flag
    payment_intent_id: str | None = None  # Last successful payment
    paid_at: datetime | None = None  # When they became premium
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User model - no changes needed
# Relationship accessed via JOIN when checking premium status
```

## API Endpoints
- `POST /api/stripe/create-checkout-session` - Create Stripe Checkout
- `POST /api/stripe/webhook` - Handle Stripe webhooks, create PremiumUser
- `POST /api/items` - Modified to check PremiumUser.is_premium and enforce limits
- `GET /api/users/me` - Modified to include premium status from PremiumUser JOIN

## Environment Variables
```bash
# Backend .env additions
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PREMIUM_PRICE_ID=price_...  # Or hardcode $1 amount

# Frontend .env additions
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...  # If needed for future features
```

## Estimated Timeline
- Phase 1: 1-2 days (database, Stripe setup, endpoints)
- Phase 2: 0.5 day (item limit logic)
- Phase 3: 1-2 days (frontend UI, checkout flow)
- Phase 4: 1 day (testing, polish, deployment prep)
- **Total**: 3.5-5.5 days for complete implementation

## Dependencies
- Stripe account (test mode for development)
- Stripe CLI for local webhook testing
- HTTPS endpoint for production webhooks
- PostgreSQL database

## Security Considerations
- Validate webhook signatures (prevent fake webhooks)
- Never trust client-side premium status
- Always verify on backend before allowing actions
- Store Stripe keys securely (environment variables)
- Use HTTPS for all Stripe communication

## Known Limitations
- One-time payment (no recurring billing)
- No refund flow (out of scope)
- No subscription management UI needed
- Manual Stripe dashboard for refunds if needed
- Premium is permanent (no downgrade flow)

## Future Enhancements (Not in This Epic)
- Subscription-based premium (monthly/yearly)
- Multiple premium tiers
- Team/organization billing
- Gifting premium to other users
- Promo codes and discounts
- Invoice generation and history
- Refund request flow

## Phase Folders
- `phase-1-backend/` - Database, Stripe API, endpoints
- `phase-2-limits/` - Item limit enforcement
- `phase-3-frontend/` - UI components and checkout flow
- `phase-4-testing/` - E2E testing and deployment

## Resources
- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Python SDK](https://stripe.com/docs/api/python)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)

## Test Cards (Stripe Test Mode)
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Requires Auth: `4000 0025 0000 3155`

---

*This epic demonstrates core Stripe integration patterns with a simple one-time payment flow. It can be extended to subscriptions and more complex billing in future epics.*
