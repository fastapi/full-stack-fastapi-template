"""Tests for billing endpoints (Stripe Checkout + Portal)."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.db import get_db
from app.api.deps import get_current_user
from kila_models.models.database import UserSubscriptionTable
from kila_models.models.base import SubscriptionTier, SubscriptionStatus


def _make_sub(
    user_id="U_test123",
    tier=SubscriptionTier.free_trial,
    status=SubscriptionStatus.active,
    stripe_customer_id=None,
    stripe_subscription_id=None,
    trial_expires_at=None,
    cancel_at_period_end=False,
):
    sub = MagicMock(spec=UserSubscriptionTable)
    sub.user_id = user_id
    sub.tier = tier
    sub.status = status
    sub.stripe_customer_id = stripe_customer_id
    sub.stripe_subscription_id = stripe_subscription_id
    sub.trial_expires_at = trial_expires_at  # explicit assignment required
    sub.cancel_at_period_end = cancel_at_period_end
    return sub


def _mock_user():
    user = MagicMock()
    user.user_id = "U_test123"
    user.email = "test@example.com"
    return user


def _mock_db(sub=None):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = sub
    db.execute.return_value = result
    return db


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_checkout_session_success():
    sub = _make_sub(stripe_customer_id=None)
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

        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/test"


@pytest.mark.asyncio
async def test_create_checkout_session_already_subscribed():
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


# ── Webhook tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_checkout_completed_uses_metadata_user_id():
    """checkout.session.completed looks up user by metadata.user_id."""
    sub = _make_sub()
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
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"user_id": "U_test123"},
                    "customer": "cus_new_123",
                    "subscription": "sub_123",
                }
            },
        }
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
            "data": {"object": {"subscription": "sub_123"}},
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

@pytest.mark.asyncio
async def test_create_checkout_session_reuses_customer_id():
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

        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert call_kwargs["customer"] == "cus_existing123"


@pytest.mark.asyncio
async def test_create_portal_session_success():
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


# ── _calculate_trial_end unit tests ──────────────────────────────────────────

from app.api.routes.billing import _calculate_trial_end


def test_calculate_trial_end_active_trial():
    """Active trial returns ceiling of remaining days."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=14)
    sub = _make_sub(trial_expires_at=expires_at, stripe_subscription_id=None)
    result = _calculate_trial_end(sub)
    assert result == 14


def test_calculate_trial_end_expired_trial():
    """Expired trial returns 0."""
    now = datetime.now(timezone.utc)
    sub = _make_sub(
        trial_expires_at=now - timedelta(days=1),
        stripe_subscription_id=None,
    )
    assert _calculate_trial_end(sub) == 0


def test_calculate_trial_end_previously_paid():
    """Previously paid user (stripe_subscription_id set) returns 0 regardless of trial_expires_at."""
    now = datetime.now(timezone.utc)
    sub = _make_sub(
        trial_expires_at=now + timedelta(days=20),
        stripe_subscription_id="sub_existing123",
    )
    assert _calculate_trial_end(sub) == 0


def test_calculate_trial_end_no_trial_record():
    """No trial record (trial_expires_at=None) and no prior payment returns 28."""
    sub = _make_sub(trial_expires_at=None, stripe_subscription_id=None)
    assert _calculate_trial_end(sub) == 28


# ── create_checkout_session trial period integration tests ────────────────────

@pytest.mark.asyncio
async def test_checkout_session_active_trial_passes_remaining_days():
    """Free trial user with 14 days left → Stripe receives trial_period_days=14."""
    now = datetime.now(timezone.utc)
    sub = _make_sub(
        trial_expires_at=now + timedelta(days=14),
        stripe_subscription_id=None,
    )
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:3000"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_pro"},
                headers={"Authorization": "Bearer test"},
            )

    assert resp.status_code == 200
    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert call_kwargs["subscription_data"]["trial_period_days"] == 14


@pytest.mark.asyncio
async def test_checkout_session_expired_trial_no_trial_period():
    """Expired trial user → Stripe does NOT receive trial_period_days."""
    now = datetime.now(timezone.utc)
    sub = _make_sub(
        trial_expires_at=now - timedelta(days=1),
        stripe_subscription_id=None,
    )
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:3000"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_pro"},
                headers={"Authorization": "Bearer test"},
            )

    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert "trial_period_days" not in call_kwargs.get("subscription_data", {})


@pytest.mark.asyncio
async def test_checkout_session_previously_paid_no_trial_period():
    """User with prior Stripe subscription → no trial_period_days (no repeat trial)."""
    now = datetime.now(timezone.utc)
    sub = _make_sub(
        trial_expires_at=now + timedelta(days=20),
        stripe_subscription_id="sub_prev123",
    )
    sub.tier = SubscriptionTier.free_trial
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:3000"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_pro"},
                headers={"Authorization": "Bearer test"},
            )

    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert "trial_period_days" not in call_kwargs.get("subscription_data", {})


@pytest.mark.asyncio
async def test_checkout_session_no_trial_record_gets_28_days():
    """New user with no trial_expires_at and no prior payment → trial_period_days=28."""
    sub = _make_sub(trial_expires_at=None, stripe_subscription_id=None)
    mock_db = _mock_db(sub)
    mock_user = _mock_user()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with (
        patch("app.api.routes.billing.stripe") as mock_stripe,
        patch("app.api.routes.billing.settings") as mock_settings,
    ):
        mock_settings.stripe_pro_price_id = "price_pro"
        mock_settings.stripe_frontend_url = "http://localhost:3000"
        mock_settings.stripe_secret_key = "sk_test_xxx"

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/v1/billing/create-checkout-session",
                json={"price_id": "price_pro"},
                headers={"Authorization": "Bearer test"},
            )

    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert call_kwargs["subscription_data"]["trial_period_days"] == 28
