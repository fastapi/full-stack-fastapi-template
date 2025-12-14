"""
Stripe API client and utilities.

Provides a configured Stripe client and helper functions for creating
checkout sessions and handling webhooks. The Stripe module is initialized
on application startup with the secret key from settings.
"""

import logging

import stripe

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_stripe() -> None:
    """
    Initialize Stripe API with secret key from settings.

    Called on application startup to configure the Stripe client.
    Must be called before any Stripe API operations.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.debug("Stripe API initialized")


def get_stripe_client() -> stripe:
    """
    Get the configured Stripe module.

    Returns the stripe module with API key already set.
    Use this for all Stripe API calls to ensure consistent configuration.

    Returns:
        stripe: The configured stripe module
    """
    return stripe
