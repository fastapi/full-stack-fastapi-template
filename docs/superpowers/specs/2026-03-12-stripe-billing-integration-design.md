# Stripe Billing Integration Design

## Overview

Integrate Stripe for subscription billing in the Kila GEO platform. Users start with a 28-day free trial, then subscribe to Basic or Pro via Stripe Checkout. Subscription management uses Stripe Customer Portal. The backend processes Stripe webhooks to keep `UserSubscriptionTable` in sync.

## Decisions

- **Checkout**: Stripe Checkout hosted page (redirect flow)
- **Subscription management**: Stripe Customer Portal (hosted by Stripe)
- **Pricing**: Monthly only (annual deferred to future iteration)
- **Expired trial behavior**: Read-only mode (can view existing data, cannot create new resources)
- **Upgrade prompts**: Dedicated pricing page + contextual modals at feature gates

## Architecture

```
User clicks "Upgrade"
  → POST /api/v1/billing/create-checkout-session { price_id }
  → Backend creates Stripe Checkout Session (metadata: user_id)
  → Returns { checkout_url }
  → Frontend redirects to Stripe
  → User pays
  → Stripe redirects to /app/billing?status=success
  → Stripe fires webhook: checkout.session.completed
  → Backend updates UserSubscriptionTable (tier, status, stripe IDs)
  → Frontend re-fetches profile → entitlements update → features unlock

User clicks "Manage Subscription"
  → POST /api/v1/billing/create-portal-session
  → Backend creates Stripe Portal Session
  → Returns { portal_url }
  → Frontend redirects to Stripe Portal
  → User cancels/updates → Stripe fires webhooks → backend updates DB
```

## Backend

### New file: `app/api/routes/billing.py`

Two endpoints, both require authentication.

#### `POST /api/v1/billing/create-checkout-session`

Request body:
```json
{ "price_id": "price_..." }
```

Logic:
1. Validate `price_id` is one of the configured Basic/Pro price IDs
2. Look up user's `UserSubscriptionTable` row
3. Reject if user already has an active paid subscription (status=active, tier != free_trial)
4. If user has existing `stripe_customer_id`, pass it as `customer`. Otherwise pass `customer_email` and let Stripe create the customer.
5. Create `stripe.checkout.Session`:
   - `mode: "subscription"`
   - `line_items: [{ price: price_id, quantity: 1 }]`
   - `success_url: {frontend_url}/app/billing?status=success`
   - `cancel_url: {frontend_url}/app/pricing?status=cancelled`
   - `metadata: { user_id }` — webhook uses this to find the subscription row
   - `subscription_data: { "metadata": { "user_id": user_id } }` — persists on the Stripe subscription object for future webhooks
6. Return `{ checkout_url: session.url }`

Response:
```json
{ "checkout_url": "https://checkout.stripe.com/..." }
```

#### `POST /api/v1/billing/create-portal-session`

No request body.

Logic:
1. Look up user's `stripe_customer_id` from `UserSubscriptionTable`
2. Return 400 if no `stripe_customer_id` exists
3. Create `stripe.billing_portal.Session`:
   - `customer: stripe_customer_id`
   - `return_url: {frontend_url}/app/billing`
4. Return `{ portal_url: session.url }`

Response:
```json
{ "portal_url": "https://billing.stripe.com/..." }
```

### Stripe SDK initialization

In `app/api/routes/billing.py`, set the API key at module level:
```python
import stripe
from app.config import settings
stripe.api_key = settings.stripe_secret_key
```

The webhook handler in `webhooks.py` already imports stripe but does not set `stripe.api_key`. Add `stripe.api_key = settings.stripe_secret_key` at module level (required for `stripe.Subscription.retrieve()` calls).

### Webhook extensions (existing `app/api/routes/webhooks.py`)

Three webhook events handled:

**`checkout.session.completed`** (existing handler — update logic):
- Extract `user_id` from `session.metadata["user_id"]` (NOT from `stripe_customer_id` lookup — the customer ID may not yet be stored on first checkout)
- Look up `UserSubscriptionTable` row by `user_id`
- Save `stripe_customer_id` from `session.customer` (this is when the customer ID is first persisted for new customers)
- Save `stripe_subscription_id` from `session.subscription`
- Map `price_id` (from `session.line_items` or subscription) to tier
- Set `status = "active"` and update `tier`

**`customer.subscription.updated`**:
- Extract `user_id` from `subscription.metadata["user_id"]`
- Extract new `price_id` from `subscription.items.data[0].price.id`
- Map `price_id` to tier using config (`stripe_basic_price_id` / `stripe_pro_price_id`)
- If `price_id` matches neither configured price, log a warning and skip the tier update (do not crash)
- Update `UserSubscriptionTable.tier`
- Handle status changes: if Stripe status is `past_due`, `canceled`, or `unpaid`, update subscription status accordingly

**`invoice.payment_failed`**:
- Extract `subscription_id` from invoice
- Find `UserSubscriptionTable` row by `stripe_subscription_id`
- Set `status = "past_due"`

### Config additions

In `app/config/base.py`, add:
```python
stripe_secret_key: str = ""
stripe_frontend_url: str = "http://localhost:5173"
```

Note: `stripe_webhook_secret`, `stripe_basic_price_id`, `stripe_pro_price_id` already exist in config.

### Route registration

Add billing router in `app/api/main.py`:
```python
from app.api.routes import billing
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
```

## Frontend

### Pricing page — `/app/pricing`

New route: `src/routes/app.pricing.tsx`
New component: `src/components/app/PricingPage.tsx`

Two plan cards side by side (Basic, Pro):
- Feature list pulled from `TIER_FEATURES` in `entitlements.ts`
- Quota list pulled from `TIER_QUOTAS` in `entitlements.ts`
- Monthly price displayed on each card (hardcoded in component — prices change rarely)
- CTA button per card:
  - If current tier matches → "Current Plan" (disabled)
  - If higher tier → "Upgrade to {Tier}" → calls `createCheckoutSession(priceId)` → `window.location.href = checkout_url`
  - If expired → "Subscribe" → same flow
- Handles `?status=success` (toast: "Subscription activated!") and `?status=cancelled` (toast: "Checkout cancelled")
- Accessible from: sidebar nav link, upgrade modal CTA

### Billing page — `/app/billing`

New route: `src/routes/app.billing.tsx`
New component: `src/components/app/BillingPage.tsx`

Displays:
- Current plan name and status
- Trial expiry date (if on trial)
- "Manage Subscription" button → calls `createPortalSession()` → `window.location.href = portal_url`
- "Change Plan" link → navigates to `/app/pricing`
- Only shows "Manage Subscription" if user has a `stripe_customer_id` (i.e., has paid before)

Handles `?status=success` query param with a success toast (returning from Stripe checkout). On success redirect, poll the profile endpoint (up to 5 seconds, 1s interval) until subscription status reflects the upgrade — this handles the race condition where the user returns before the webhook has been processed.

### Upgrade modal

New component: `src/components/app/UpgradeModal.tsx`

- Reusable dialog triggered by `FeatureGate` and `QuotaGate` when user lacks access
- Content: message about what feature/quota requires upgrade + "View Plans" button → navigates to `/app/pricing`
- Replaces or wraps the existing gate behavior (currently gates just hide content)

### API client — `src/clients/billing.ts`

```typescript
export async function createCheckoutSession(priceId: string): Promise<{ checkout_url: string }>
export async function createPortalSession(): Promise<{ portal_url: string }>
```

Uses same auth headers pattern as existing clients.

### Nav updates

In `AppLayout.tsx` sidebar:
- Add "Pricing" link (visible to all users)
- Add "Billing" link (visible to users with active paid subscriptions)

## Required changes to existing code

- `kila-models` `SubscriptionStatus` enum — add `PAST_DUE = "past_due"` (see Status enum extension section)
- `kila/frontend/src/lib/entitlements.ts` — add `"past_due"` to `SubscriptionStatus` type
- `kila/frontend/src/components/app/FeatureGate.tsx` — fix link from `/pricing` to `/app/pricing`
- `kila/backend/app/api/routes/webhooks.py` — add `stripe.api_key = settings.stripe_secret_key` at module level (required for `stripe.Subscription.retrieve()` calls); update `checkout.session.completed` handler to look up user by `metadata.user_id`; add `customer.subscription.updated` and `invoice.payment_failed` handlers

## Existing code — no changes needed

- `UserSubscriptionTable` — table columns already have all needed fields (`stripe_customer_id`, `stripe_subscription_id`, `tier`, `status`)
- `useEntitlement` hook — already checks tier, features, quotas, expiry
- `SubscriptionContext` — already loads subscription from profile endpoint
- `QuotaGate` — already wraps gated content
- Auth system — unchanged
- Profile endpoint — already returns subscription data

## Configuration

Environment variables in `.env.development`:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_BASIC_PRICE_ID=price_1TAEqDH3eU9i5HkBIWUezHE8
STRIPE_PRO_PRICE_ID=price_1TAEtNH3eU9i5HkBRF6lPHJt
STRIPE_FRONTEND_URL=http://localhost:5173
```

## Testing

### Unit tests (mocked Stripe SDK)

- `test_create_checkout_session` — correct Stripe params, returns URL
- `test_create_checkout_session_already_subscribed` — rejects active paid users
- `test_create_checkout_session_reuses_customer_id` — passes existing customer ID
- `test_create_portal_session` — creates portal session, returns URL
- `test_create_portal_session_no_customer` — returns 400
- `test_webhook_subscription_updated` — tier changes correctly
- `test_webhook_payment_failed` — status set to past_due

### Manual E2E testing

1. Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
2. Forward webhooks: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe`
3. Test flow: signup → free trial → upgrade via checkout (card: 4242 4242 4242 4242) → verify subscription active → manage via portal → cancel → verify read-only mode

## Status enum extension

Add `past_due` to the `SubscriptionStatus` enum in `kila-models`:
```python
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
```

Add `past_due` to the frontend `SubscriptionStatus` type in `src/lib/entitlements.ts`:
```typescript
type SubscriptionStatus = "active" | "expired" | "cancelled" | "past_due"
```

This requires an Alembic migration with explicit MySQL enum alteration:
```python
# In the migration's upgrade():
op.execute("ALTER TABLE user_subscriptions MODIFY COLUMN status ENUM('active','expired','cancelled','past_due') NOT NULL DEFAULT 'active'")

# In the migration's downgrade():
op.execute("ALTER TABLE user_subscriptions MODIFY COLUMN status ENUM('active','expired','cancelled') NOT NULL DEFAULT 'active'")
```

## Future iterations

- Annual pricing (monthly + annual toggle on pricing page)
- Custom subscription management UI (replace Stripe Portal)
- Usage-based billing
- Invoice history page
