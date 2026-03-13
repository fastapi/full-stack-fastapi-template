# Stripe Billing Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Stripe Checkout and Customer Portal for subscription billing, keeping `UserSubscriptionTable` in sync via webhooks.

**Architecture:** Backend adds two billing endpoints (create-checkout-session, create-portal-session) and extends the existing webhook handler. Frontend adds pricing page, billing page, upgrade modal, and billing API client. The `SubscriptionStatus` enum gets a `past_due` value via Alembic migration.

**Tech Stack:** Stripe Python SDK, FastAPI, PostgreSQL (Alembic migrations), React 19, TanStack Router, Tailwind CSS 4, shadcn/ui

**Spec:** `docs/superpowers/specs/2026-03-12-stripe-billing-integration-design.md`

---

## Chunk 1: Backend — Config, Enum, Migration, Billing Endpoints

### Task 1: Add config fields and Stripe API key initialization

**Files:**
- Modify: `kila/backend/app/config/base.py:60-63`

- [ ] **Step 1: Add `stripe_secret_key` and `stripe_frontend_url` to config**

In `kila/backend/app/config/base.py`, add two fields after line 63 (after `stripe_pro_price_id`):

```python
    stripe_secret_key: str = ""
    stripe_frontend_url: str = "http://localhost:5173"
```

The `# Stripe` section (lines 60-63) should become:

```python
    # Stripe
    stripe_webhook_secret: str = ""
    stripe_basic_price_id: str = ""
    stripe_pro_price_id: str = ""
    stripe_secret_key: str = ""
    stripe_frontend_url: str = "http://localhost:5173"
```

- [ ] **Step 2: Add env vars to `.env.development`**

In `kila/backend/.env.development`, add placeholder entries (developers fill in real values locally — do NOT commit real keys):

```
STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_FRONTEND_URL=http://localhost:5173
STRIPE_BASIC_PRICE_ID=price_replace_me_basic
STRIPE_PRO_PRICE_ID=price_replace_me_pro
```

Note: `STRIPE_WEBHOOK_SECRET` will be set after running `stripe listen` locally. Real test keys should be set in each developer's local `.env.development` (which should be in `.gitignore`).

- [ ] **Step 3: Commit**

```bash
cd kila
git add backend/app/config/base.py
git commit -m "feat(billing): add Stripe config fields (secret key, frontend URL)"
```

---

### Task 2: Add `past_due` to SubscriptionStatus enum

**Files:**
- Modify: `kila-models/src/kila_models/models/base.py:60-63`
- Modify: `kila/frontend/src/lib/entitlements.ts:7`

- [ ] **Step 1: Add `past_due` to Python enum**

In `kila-models/src/kila_models/models/base.py`, the `SubscriptionStatus` enum (lines 60-63) should become:

```python
class SubscriptionStatus(str, Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    past_due = "past_due"
```

- [ ] **Step 2: Add `past_due` to frontend type**

In `kila/frontend/src/lib/entitlements.ts`, change line 7 from:

```typescript
export type SubscriptionStatus = "active" | "expired" | "cancelled"
```

to:

```typescript
export type SubscriptionStatus = "active" | "expired" | "cancelled" | "past_due"
```

- [ ] **Step 3: Update `useEntitlement` hook to handle `past_due`**

In `kila/frontend/src/hooks/useEntitlement.ts`, line 38. Change:

```typescript
  const isReadOnly = isSuperUser ? false : isExpired || status === "cancelled"
```

to:

```typescript
  const isReadOnly = isSuperUser ? false : isExpired || status === "cancelled" || status === "past_due"
```

- [ ] **Step 4: Commit**

```bash
cd kila-models && git add src/kila_models/models/base.py && git commit -m "feat: add past_due to SubscriptionStatus enum"
cd ../kila && git add frontend/src/lib/entitlements.ts frontend/src/hooks/useEntitlement.ts && git commit -m "feat: add past_due to SubscriptionStatus type and useEntitlement hook"
```

---

### Task 3: Alembic migration for `past_due` enum value

**Files:**
- Create: `kila/backend/app/alembic/versions/<auto>_add_past_due_subscription_status.py`

- [ ] **Step 1: Create migration file**

```bash
cd kila/backend
alembic revision -m "add_past_due_subscription_status"
```

- [ ] **Step 2: Edit the generated migration**

Replace the `upgrade()` and `downgrade()` functions with:

```python
def upgrade() -> None:
    # PostgreSQL: add 'past_due' to the subscriptionstatus enum type
    op.execute("ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'past_due'")


def downgrade() -> None:
    # PostgreSQL enums cannot easily remove values.
    # This is a one-way migration. To fully revert, recreate the enum type.
    pass
```

Note: PostgreSQL `ALTER TYPE ... ADD VALUE` cannot run inside a transaction. Alembic's `--transaction-per-migration` may need to be disabled. If Alembic errors, add `from alembic import context` and wrap:

```python
def upgrade() -> None:
    if not context.is_offline_mode():
        context.get_context().connection.execution_options(isolation_level="AUTOCOMMIT")
    op.execute("ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'past_due'")
```

- [ ] **Step 3: Apply migration**

```bash
cd kila/backend
alembic upgrade head
```

- [ ] **Step 4: Commit**

```bash
cd kila
git add backend/app/alembic/versions/
git commit -m "feat(billing): add past_due to subscriptionstatus enum via migration"
```

---

### Task 4: Create billing API endpoints

**Files:**
- Create: `kila/backend/app/api/routes/billing.py`
- Modify: `kila/backend/app/api/main.py:1-19`

- [ ] **Step 1: Write tests for billing endpoints**

Create `kila/backend/tests/api/routes/test_billing.py`:

```python
"""Tests for billing endpoints (Stripe Checkout + Portal)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.db import get_db
from app.api.deps import get_current_user
from kila_models.models.database import UserSubscriptionTable
from kila_models.models.base import SubscriptionTier, SubscriptionStatus


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_sub(
    user_id="U_test123",
    tier=SubscriptionTier.free_trial,
    status=SubscriptionStatus.active,
    stripe_customer_id=None,
    stripe_subscription_id=None,
):
    """Create a mock UserSubscriptionTable row."""
    sub = MagicMock(spec=UserSubscriptionTable)
    sub.user_id = user_id
    sub.tier = tier
    sub.status = status
    sub.stripe_customer_id = stripe_customer_id
    sub.stripe_subscription_id = stripe_subscription_id
    return sub


def _mock_user():
    user = MagicMock()
    user.user_id = "U_test123"
    user.email = "test@example.com"
    return user


def _mock_db(sub=None):
    """Create an async mock DB session that returns `sub` from scalar_one_or_none."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = sub
    db.execute.return_value = result
    return db


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    """Clean up FastAPI dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


# ── create-checkout-session ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_checkout_session_success():
    """Creates a Stripe checkout session and returns the URL."""
    sub = _make_sub(stripe_customer_id=None)
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    # Use FastAPI dependency overrides (not module patches) for DI
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:5173"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_basic"},
                headers={"Authorization": "Bearer test"},
            )

        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/test"


@pytest.mark.asyncio
async def test_create_checkout_session_already_subscribed():
    """Rejects users who already have an active paid subscription."""
    sub = _make_sub(tier=SubscriptionTier.basic, status=SubscriptionStatus.active)
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with patch("app.api.routes.billing.settings") as mock_settings:
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_basic"},
                headers={"Authorization": "Bearer test"},
            )

        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_checkout_session_reuses_customer_id():
    """Passes existing stripe_customer_id to Stripe when available."""
    sub = _make_sub(stripe_customer_id="cus_existing123")
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:5173"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_basic"},
                headers={"Authorization": "Bearer test"},
            )

        # Verify customer param was passed
        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert call_kwargs["customer"] == "cus_existing123"


# ── create-portal-session ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_portal_session_success():
    """Creates portal session for users with stripe_customer_id."""
    sub = _make_sub(stripe_customer_id="cus_123")
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_frontend_url = "http://localhost:5173"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_portal = MagicMock()
        mock_portal.url = "https://billing.stripe.com/test"
        mock_stripe.billing_portal.Session.create.return_value = mock_portal

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-portal-session",
                headers={"Authorization": "Bearer test"},
            )

        assert resp.status_code == 200
        assert resp.json()["portal_url"] == "https://billing.stripe.com/test"


@pytest.mark.asyncio
async def test_create_portal_session_no_customer():
    """Returns 400 when user has no stripe_customer_id."""
    sub = _make_sub(stripe_customer_id=None)
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with patch("app.api.routes.billing.settings") as mock_settings:
        mock_settings.stripe_secret_key = "sk_test_xxx"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-portal-session",
                headers={"Authorization": "Bearer test"},
            )

        assert resp.status_code == 400
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd kila/backend
uv run pytest tests/api/routes/test_billing.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.api.routes.billing'`

- [ ] **Step 3: Create `billing.py` with endpoints**

Create `kila/backend/app/api/routes/billing.py`:

```python
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

    # Look up user's subscription
    stmt = select(UserSubscriptionTable).where(
        UserSubscriptionTable.user_id == current_user.user_id
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")

    # Reject if already on an active paid plan
    if (
        sub.status == SubscriptionStatus.active
        and sub.tier != SubscriptionTier.free_trial
    ):
        raise HTTPException(
            status_code=400, detail="Already have an active paid subscription"
        )

    # Build Stripe Checkout params
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
```

- [ ] **Step 4: Register billing router**

In `kila/backend/app/api/main.py`, add after line 8:

```python
from app.api.routes import billing
```

And after line 19 (after the webhooks router):

```python
api_router.include_router(billing.router, tags=["billing"])
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd kila/backend
uv run pytest tests/api/routes/test_billing.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd kila
git add backend/app/api/routes/billing.py backend/app/api/main.py backend/tests/api/routes/test_billing.py
git commit -m "feat(billing): add Stripe checkout and portal session endpoints"
```

---

### Task 5: Update webhook handler

**Files:**
- Modify: `kila/backend/app/api/routes/webhooks.py`

- [ ] **Step 1: Write tests for new webhook events**

Add to `kila/backend/tests/api/routes/test_billing.py` (append):

```python
# ── Webhook tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_checkout_completed_uses_metadata_user_id():
    """checkout.session.completed looks up user by metadata.user_id, not stripe_customer_id."""
    sub = _make_sub()
    mock_db = _mock_db(sub)

    # Webhooks don't use get_current_user, but do use get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.webhooks.stripe") as mock_stripe,
        patch("app.api.routes.webhooks.settings") as mock_settings,
    ):
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"

        mock_stripe.Webhook.construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"user_id": "U_test123"},
                    "customer": "cus_new_123",
                    "subscription": "sub_123",
                }
            },
        }
        # Use a dict for the subscription response (webhook code uses bracket notation)
        mock_stripe.Subscription.retrieve.return_value = {
            "items": {"data": [{"price": {"id": "price_basic"}}]}
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/webhooks/stripe",
                content=b"test_payload",
                headers={"stripe-signature": "test_sig"},
            )

        assert resp.status_code == 200
        # sub should have stripe_customer_id set
        assert sub.stripe_customer_id == "cus_new_123"


@pytest.mark.asyncio
async def test_webhook_subscription_updated():
    """customer.subscription.updated changes tier correctly."""
    sub = _make_sub(tier=SubscriptionTier.basic, status=SubscriptionStatus.active)
    mock_db = _mock_db(sub)

    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.webhooks.stripe") as mock_stripe,
        patch("app.api.routes.webhooks.settings") as mock_settings,
    ):
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"

        mock_stripe.Webhook.construct_event.return_value = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "metadata": {"user_id": "U_test123"},
                    "status": "active",
                    "items": {"data": [{"price": {"id": "price_pro"}}]},
                }
            },
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/webhooks/stripe",
                content=b"test_payload",
                headers={"stripe-signature": "test_sig"},
            )

        assert resp.status_code == 200
        assert sub.tier == SubscriptionTier.pro


@pytest.mark.asyncio
async def test_webhook_payment_failed():
    """invoice.payment_failed sets status to past_due."""
    sub = _make_sub(
        tier=SubscriptionTier.basic,
        status=SubscriptionStatus.active,
        stripe_subscription_id="sub_123",
    )
    mock_db = _mock_db(sub)

    app.dependency_overrides[get_db] = lambda: mock_db

    with (
        patch("app.api.routes.webhooks.stripe") as mock_stripe,
        patch("app.api.routes.webhooks.settings") as mock_settings,
    ):
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_basic_price_id = "price_basic"
        mock_settings.stripe_pro_price_id = "price_pro"

        mock_stripe.Webhook.construct_event.return_value = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "subscription": "sub_123",
                }
            },
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/webhooks/stripe",
                content=b"test_payload",
                headers={"stripe-signature": "test_sig"},
            )

        assert resp.status_code == 200
        assert sub.status == SubscriptionStatus.past_due
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd kila/backend
uv run pytest tests/api/routes/test_billing.py -v -k "webhook"
```

Expected: FAIL — webhook handlers don't exist yet for `customer.subscription.updated` and `invoice.payment_failed`.

- [ ] **Step 3: Update webhooks.py**

Replace the entire contents of `kila/backend/app/api/routes/webhooks.py` with:

```python
"""Stripe webhook handler — keeps UserSubscriptionTable in sync."""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.db import get_db
from kila_models.models.base import SubscriptionStatus, SubscriptionTier
from kila_models.models.database import UserSubscriptionTable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.stripe_secret_key


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
            logger.warning(f"Unknown price_id in subscription.updated: {price_id}, skipping tier update")

        # Map Stripe status to our status
        if stripe_status == "past_due":
            sub.status = SubscriptionStatus.past_due
        elif stripe_status == "canceled" or stripe_status == "unpaid":
            sub.status = SubscriptionStatus.cancelled
        elif stripe_status == "active":
            sub.status = SubscriptionStatus.active

        await db.commit()
        logger.info(f"Updated subscription {sub.subscription_id}: tier={sub.tier}, status={sub.status}")

    elif event_type == "customer.subscription.deleted":
        customer_id = data_object.get("customer")

        stmt = select(UserSubscriptionTable).where(
            UserSubscriptionTable.stripe_customer_id == customer_id
        )
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = SubscriptionStatus.cancelled
            await db.commit()
            logger.info(f"Cancelled subscription {sub.subscription_id}")

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
```

- [ ] **Step 4: Run all tests**

```bash
cd kila/backend
uv run pytest tests/api/routes/test_billing.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd kila
git add backend/app/api/routes/webhooks.py backend/tests/api/routes/test_billing.py
git commit -m "feat(billing): update webhook handler with user_id lookup and new events"
```

---

## Chunk 2: Frontend — Billing Client, Pages, Nav Updates

### Task 6: Create billing API client

**Files:**
- Create: `kila/frontend/src/clients/billing.ts`

- [ ] **Step 1: Create billing API client**

Create `kila/frontend/src/clients/billing.ts`:

```typescript
import { getAuthToken } from "./auth-helper"

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

class BillingAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  async createCheckoutSession(
    priceId: string,
  ): Promise<{ checkout_url: string }> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/billing/create-checkout-session`,
      {
        method: "POST",
        headers: await this.getAuthHeaders(),
        body: JSON.stringify({ price_id: priceId }),
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create checkout session")
    }

    return response.json()
  }

  async createPortalSession(): Promise<{ portal_url: string }> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/billing/create-portal-session`,
      {
        method: "POST",
        headers: await this.getAuthHeaders(),
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create portal session")
    }

    return response.json()
  }
}

export const billingAPI = new BillingAPI()
```

- [ ] **Step 2: Commit**

```bash
cd kila
git add frontend/src/clients/billing.ts
git commit -m "feat(billing): add billing API client for checkout and portal sessions"
```

---

### Task 7: Create Pricing page

**Files:**
- Create: `kila/frontend/src/routes/app.pricing.tsx`
- Create: `kila/frontend/src/components/app/PricingPage.tsx`

- [ ] **Step 1: Create the route file**

Create `kila/frontend/src/routes/app.pricing.tsx`:

```typescript
import { createFileRoute } from "@tanstack/react-router"
import { PricingPage } from "@/components/app/PricingPage"

export const Route = createFileRoute("/app/pricing")({
  component: PricingPage,
})
```

- [ ] **Step 2: Create the PricingPage component**

Create `kila/frontend/src/components/app/PricingPage.tsx`:

```tsx
import { useNavigate } from "@tanstack/react-router"
import { Check, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { billingAPI } from "@/clients/billing"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useEntitlement } from "@/hooks/useEntitlement"
import {
  type SubscriptionTier,
  TIER_FEATURES,
  TIER_QUOTAS,
} from "@/lib/entitlements"

const PLANS: {
  tier: SubscriptionTier
  name: string
  price: string
  priceId: string
  description: string
}[] = [
  {
    tier: "basic",
    name: "Basic",
    price: "$29",
    priceId: import.meta.env.VITE_STRIPE_BASIC_PRICE_ID ?? "",
    description: "For individuals getting started with AI brand monitoring",
  },
  {
    tier: "pro",
    name: "Pro",
    price: "$79",
    priceId: import.meta.env.VITE_STRIPE_PRO_PRICE_ID ?? "",
    description: "For teams needing full competitive intelligence",
  },
]

function getFeatureLabels(tier: SubscriptionTier): string[] {
  const features = TIER_FEATURES[tier]
  const quotas = TIER_QUOTAS[tier]
  const labels: string[] = []

  labels.push(`${quotas.brands} brand${quotas.brands > 1 ? "s" : ""}`)
  labels.push(
    `${quotas.segmentsPerBrand} segment${quotas.segmentsPerBrand > 1 ? "s" : ""} per brand`,
  )
  labels.push(
    `${quotas.promptsPerSegment} prompt${quotas.promptsPerSegment > 1 ? "s" : ""} per segment`,
  )

  if (features.brandImpression) labels.push("Brand Impression analytics")
  if (features.competitiveAnalysisFull) labels.push("Full Competitive Analysis")
  if (features.insightBrandRisk) labels.push("Brand Risk insights")
  if (features.insightAll) labels.push("All insight pages")

  return labels
}

export function PricingPage() {
  const { tier: currentTier, isExpired, isReadOnly } = useEntitlement()
  const [loadingPriceId, setLoadingPriceId] = useState<string | null>(null)
  const navigate = useNavigate()

  // Handle query params from Stripe redirect
  const searchParams = new URLSearchParams(window.location.search)
  const statusParam = searchParams.get("status")

  useEffect(() => {
    if (statusParam === "cancelled") {
      toast.info("Checkout cancelled")
      // Clean up URL
      navigate({ to: "/app/pricing", replace: true })
    }
  }, [statusParam, navigate])

  const handleUpgrade = async (priceId: string) => {
    try {
      setLoadingPriceId(priceId)
      const { checkout_url } = await billingAPI.createCheckoutSession(priceId)
      window.location.href = checkout_url
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to start checkout",
      )
    } finally {
      setLoadingPriceId(null)
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Choose Your Plan</h1>
        <p className="mt-2 text-sm text-slate-500">
          Unlock powerful AI brand monitoring and competitive intelligence
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {PLANS.map((plan) => {
          const isCurrent =
            currentTier === plan.tier && !isExpired && !isReadOnly
          const isLoading = loadingPriceId === plan.priceId

          return (
            <Card
              key={plan.tier}
              className={`relative ${plan.tier === "pro" ? "border-blue-500 shadow-lg" : ""}`}
            >
              {plan.tier === "pro" && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="mt-2">
                  <span className="text-3xl font-bold text-slate-900">
                    {plan.price}
                  </span>
                  <span className="text-sm text-slate-500">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {getFeatureLabels(plan.tier).map((label) => (
                    <li key={label} className="flex items-start gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                      <span className="text-slate-700">{label}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.tier === "pro" ? "default" : "outline"}
                  disabled={isCurrent || isLoading}
                  onClick={() => handleUpgrade(plan.priceId)}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  {isCurrent
                    ? "Current Plan"
                    : isExpired || isReadOnly
                      ? "Subscribe"
                      : `Upgrade to ${plan.name}`}
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Add frontend env vars**

In `kila/frontend/.env` (or `.env.development`), add:

```
VITE_STRIPE_BASIC_PRICE_ID=price_1TAEqDH3eU9i5HkBIWUezHE8
VITE_STRIPE_PRO_PRICE_ID=price_1TAEtNH3eU9i5HkBRF6lPHJt
```

- [ ] **Step 4: Regenerate route tree**

```bash
cd kila/frontend
pnpm dev &
# Wait for TanStack Router to regenerate routeTree.gen.ts, then stop
# Or run: npx tsr generate
```

- [ ] **Step 5: Verify page renders**

Open `http://localhost:5173/app/pricing` in browser. Should show two plan cards.

- [ ] **Step 6: Commit**

```bash
cd kila
git add frontend/src/routes/app.pricing.tsx frontend/src/components/app/PricingPage.tsx frontend/src/routeTree.gen.ts
git commit -m "feat(billing): add pricing page with plan cards and checkout flow"
```

---

### Task 8: Create Billing page

**Files:**
- Create: `kila/frontend/src/routes/app.billing.tsx`
- Create: `kila/frontend/src/components/app/BillingPage.tsx`

- [ ] **Step 1: Create the route file**

Create `kila/frontend/src/routes/app.billing.tsx`:

```typescript
import { createFileRoute } from "@tanstack/react-router"
import { BillingPage } from "@/components/app/BillingPage"

export const Route = createFileRoute("/app/billing")({
  component: BillingPage,
})
```

- [ ] **Step 2: Create the BillingPage component**

Create `kila/frontend/src/components/app/BillingPage.tsx`:

```tsx
import { useNavigate } from "@tanstack/react-router"
import { CreditCard, ExternalLink, Loader2 } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"
import { billingAPI } from "@/clients/billing"
import { profileAPI } from "@/clients/profile"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { useEntitlement } from "@/hooks/useEntitlement"
import { TIER_NAMES } from "@/lib/entitlements"

export function BillingPage() {
  const { subscription } = useSubscription()
  const { tier, isExpired, isReadOnly } = useEntitlement()
  const navigate = useNavigate()
  const [portalLoading, setPortalLoading] = useState(false)
  const pollingRef = useRef(false)

  // Handle success redirect from Stripe Checkout
  const searchParams = new URLSearchParams(window.location.search)
  const statusParam = searchParams.get("status")

  useEffect(() => {
    if (statusParam !== "success" || pollingRef.current) return
    pollingRef.current = true

    // Poll profile endpoint to wait for webhook processing
    let attempts = 0
    const maxAttempts = 5
    const poll = setInterval(async () => {
      attempts++
      try {
        const profile = await profileAPI.getProfile()
        const sub = (profile as any)?.subscription
        if (sub && sub.tier !== "free_trial" && sub.status === "active") {
          clearInterval(poll)
          toast.success("Subscription activated!")
          // Force page reload to refresh SubscriptionContext
          window.location.replace("/app/billing")
          return
        }
      } catch {
        // ignore fetch errors during polling
      }
      if (attempts >= maxAttempts) {
        clearInterval(poll)
        toast.success("Subscription activated! It may take a moment to reflect.")
        window.location.replace("/app/billing")
      }
    }, 1000)

    return () => clearInterval(poll)
  }, [statusParam])

  const handleManageSubscription = async () => {
    try {
      setPortalLoading(true)
      const { portal_url } = await billingAPI.createPortalSession()
      window.location.href = portal_url
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to open billing portal",
      )
    } finally {
      setPortalLoading(false)
    }
  }

  // Heuristic: show "Manage Subscription" if user is on a paid tier or was previously
  // (stripe_customer_id is not exposed to frontend, so we check tier as proxy)
  const hasStripeCustomer = tier !== "free_trial"

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Billing</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Subscription
          </CardTitle>
          <CardDescription>Manage your subscription and billing</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <span className="text-sm text-slate-500">Current Plan</span>
            <span className="text-sm font-medium text-slate-900">
              {TIER_NAMES[tier]}
            </span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <span className="text-sm text-slate-500">Status</span>
            <span
              className={`text-sm font-medium ${
                isExpired || isReadOnly
                  ? "text-red-600"
                  : subscription?.status === "past_due"
                    ? "text-amber-600"
                    : "text-green-600"
              }`}
            >
              {subscription?.status === "past_due"
                ? "Past Due"
                : isExpired
                  ? "Expired"
                  : isReadOnly
                    ? "Cancelled"
                    : "Active"}
            </span>
          </div>

          {subscription?.trial_expires_at && tier === "free_trial" && (
            <div className="flex items-center justify-between py-2 border-b border-slate-100">
              <span className="text-sm text-slate-500">Trial Expires</span>
              <span className="text-sm font-medium text-slate-900">
                {new Date(subscription.trial_expires_at).toLocaleDateString()}
              </span>
            </div>
          )}

          <div className="flex flex-col gap-2 pt-2">
            {hasStripeCustomer && (
              <Button
                variant="outline"
                onClick={handleManageSubscription}
                disabled={portalLoading}
              >
                {portalLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <ExternalLink className="h-4 w-4 mr-2" />
                )}
                Manage Subscription
              </Button>
            )}

            <Button
              variant="ghost"
              onClick={() => navigate({ to: "/app/pricing" })}
            >
              {isExpired || isReadOnly ? "Subscribe" : "Change Plan"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 3: Regenerate route tree**

```bash
cd kila/frontend
npx tsr generate
```

- [ ] **Step 4: Verify page renders**

Open `http://localhost:5173/app/billing` in browser. Should show current plan info.

- [ ] **Step 5: Commit**

```bash
cd kila
git add frontend/src/routes/app.billing.tsx frontend/src/components/app/BillingPage.tsx frontend/src/routeTree.gen.ts
git commit -m "feat(billing): add billing page with subscription management"
```

---

### Task 9: Create UpgradeModal and fix FeatureGate link

**Files:**
- Create: `kila/frontend/src/components/app/UpgradeModal.tsx`
- Modify: `kila/frontend/src/components/app/FeatureGate.tsx:51-56`

- [ ] **Step 1: Create UpgradeModal component**

Create `kila/frontend/src/components/app/UpgradeModal.tsx`:

```tsx
import { useNavigate } from "@tanstack/react-router"
import { Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface UpgradeModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  message?: string
}

export function UpgradeModal({
  open,
  onOpenChange,
  message = "Upgrade your plan to access this feature.",
}: UpgradeModalProps) {
  const navigate = useNavigate()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto mb-2 rounded-full bg-slate-100 p-3">
            <Lock className="h-6 w-6 text-slate-500" />
          </div>
          <DialogTitle className="text-center">Upgrade Required</DialogTitle>
          <DialogDescription className="text-center">
            {message}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-center">
          <Button
            onClick={() => {
              onOpenChange(false)
              navigate({ to: "/app/pricing" })
            }}
          >
            View Plans
          </Button>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Maybe Later
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

- [ ] **Step 2: Fix FeatureGate link**

In `kila/frontend/src/components/app/FeatureGate.tsx`, change line 52 from:

```tsx
            href="/pricing"
```

to:

```tsx
            href="/app/pricing"
```

- [ ] **Step 3: Commit**

```bash
cd kila
git add frontend/src/components/app/UpgradeModal.tsx frontend/src/components/app/FeatureGate.tsx
git commit -m "feat(billing): add UpgradeModal and fix FeatureGate pricing link"
```

---

### Task 10: Add Pricing and Billing links to sidebar nav + fix AppLayout pricing link

**Files:**
- Modify: `kila/frontend/src/components/app/AppLayout.tsx:3-18` (imports), `61-91` (menu items), and trial expiry banner

- [ ] **Step 1: Add nav items and fix trial expiry link**

In `kila/frontend/src/components/app/AppLayout.tsx`:

1. Add imports at the top (after existing lucide imports):

```typescript
import { CreditCard, DollarSign } from "lucide-react"
```

2. In the `menuItems` array (around line 61-91), add before `{ name: "My Profile", ... }`:

```typescript
    { name: "Pricing", icon: DollarSign, path: "/app/pricing" },
```

3. Build the Billing link conditionally. After the `menuItems` array, add:

```typescript
  // Only show Billing if user has a paid subscription (past or present)
  const allMenuItems = [
    ...menuItems.slice(0, -1), // everything except "My Profile"
    ...(currentTier !== "free_trial"
      ? [{ name: "Billing", icon: CreditCard, path: "/app/billing" } as MenuItem]
      : []),
    menuItems[menuItems.length - 1], // "My Profile" last
  ]
```

Then use `allMenuItems` instead of `menuItems` wherever the menu is rendered in the component.

Note: This requires access to the current tier. The component already calls `useEntitlement()` on line 56 — destructure `tier` as well:

```typescript
  const { isExpired, canAccess, tier: currentTier } = useEntitlement()
```

4. Fix the trial expiry banner link. Find `href="/pricing"` in the trial expiry banner (around line 409) and change to `href="/app/pricing"`.

- [ ] **Step 2: Verify nav renders**

Open the app in browser. "Pricing" link should always appear. "Billing" link should only appear for paid users.

- [ ] **Step 3: Commit**

```bash
cd kila
git add frontend/src/components/app/AppLayout.tsx
git commit -m "feat(billing): add Pricing/Billing nav links and fix /pricing paths"
```

---

## Chunk 3: Integration Testing and Verification

### Task 11: Manual E2E testing with Stripe CLI

No files to create — verification only.

- [ ] **Step 1: Start backend**

```bash
cd kila/backend
ENVIRONMENT=development uvicorn app.main:app --reload
```

- [ ] **Step 2: Start frontend**

```bash
cd kila/frontend
pnpm dev
```

- [ ] **Step 3: Start Stripe webhook forwarding**

```bash
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

Copy the webhook signing secret (`whsec_...`) and add it to `kila/backend/.env.development`:

```
STRIPE_WEBHOOK_SECRET=whsec_...
```

Restart the backend after updating `.env.development`.

- [ ] **Step 4: Test checkout flow**

1. Sign up or log in
2. Navigate to `/app/pricing`
3. Click "Upgrade to Basic"
4. On Stripe Checkout, use test card: `4242 4242 4242 4242`, any future expiry, any CVC
5. After redirect, verify subscription status changed to "active" on `/app/billing`
6. Verify tier updated in the profile endpoint

- [ ] **Step 5: Test portal flow**

1. On `/app/billing`, click "Manage Subscription"
2. Verify redirect to Stripe Customer Portal
3. Cancel the subscription in the portal
4. Return to app — verify status shows "Cancelled" and app is read-only

- [ ] **Step 6: Test payment failure**

In Stripe Dashboard, trigger an `invoice.payment_failed` test event. Verify subscription status changes to "past_due" and app shows read-only mode.

- [ ] **Step 7: Run all backend tests**

```bash
cd kila/backend
bash scripts/test.sh
```

Expected: All tests pass.

- [ ] **Step 8: Run frontend build**

```bash
cd kila/frontend
pnpm build
```

Expected: Build succeeds with no TypeScript errors.
