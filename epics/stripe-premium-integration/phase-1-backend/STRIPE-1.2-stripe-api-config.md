# STRIPE-1.2: Stripe API Configuration

## Status: COMPLETE

## Summary
Set up Stripe Python SDK and configuration, including environment variables and a utility module for Stripe operations.

## Acceptance Criteria
- [x] stripe Python package installed in backend (v14.0.1)
- [x] Environment variables added to .env and config
- [x] Stripe utility module created at `backend/app/premium_users/stripe.py` (changed from core/)
- [x] Stripe client initializes successfully on app startup
- [ ] Configuration validates Stripe keys are present (deferred - using placeholder keys)

## Technical Details

### Install Stripe Package
```bash
# Inside backend container or with uv
uv add stripe
```

### Environment Variables
Add to `backend/.env`:
```bash
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PREMIUM_PRICE_CENTS=100  # $1.00 in cents
```

### Update Settings
Modify `backend/app/core/config.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Stripe Configuration
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PREMIUM_PRICE_CENTS: int = 100  # Default $1.00
```

### Create Stripe Utility Module
Create `backend/app/core/stripe.py`:
```python
"""
Stripe API client and utilities.

This module provides a configured Stripe client and helper functions
for creating checkout sessions and handling webhooks.
"""
import logging

import stripe
from app.core.config import settings

logger = logging.getLogger(__name__)


def init_stripe() -> None:
    """
    Initialize Stripe API with secret key.

    Called on application startup to configure the Stripe client.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.info("Stripe API initialized")


def get_stripe_client() -> stripe:
    """
    Get configured Stripe module.

    Returns the stripe module with API key already set.
    Use for all Stripe API calls.
    """
    return stripe
```

### Initialize on App Startup
Modify `backend/app/main.py`:
```python
from app.core.stripe import init_stripe

# In app startup or after app creation
init_stripe()
```

### Files to Create/Modify
1. `backend/pyproject.toml` - Add stripe dependency
2. `backend/.env` - Add Stripe environment variables
3. `backend/app/core/config.py` - Add Stripe settings
4. `backend/app/core/stripe.py` - Create new file
5. `backend/app/main.py` - Initialize Stripe on startup

## Dependencies
- STRIPE-1.1 (model should exist, but not strictly required)

## Testing
- [ ] App starts without errors with valid Stripe keys
- [ ] App fails gracefully if Stripe keys missing
- [ ] Can import stripe module in Python shell
- [ ] `stripe.api_key` is set after init

## Getting Stripe Test Keys
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy "Secret key" (starts with `sk_test_`)
3. For webhook secret, will be generated when setting up webhook endpoint

## Notes
- NEVER commit real Stripe keys to git
- Use `sk_test_` keys for development (test mode)
- Webhook secret (`whsec_`) comes from Stripe CLI or dashboard
- Keep price in cents to avoid floating point issues
