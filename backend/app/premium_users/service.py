"""
Premium user service functions.

Provides helper functions for checking premium status and enforcing
feature limits throughout the application. These functions are used
by API endpoints to gate features based on user tier.
"""

import logging
import uuid

from sqlmodel import Session, func, select

from app.models import Item, User
from app.premium_users.models import PremiumUser

logger = logging.getLogger(__name__)

FREE_TIER_ITEM_LIMIT = 2


def is_user_premium(session: Session, user_id: uuid.UUID) -> bool:
    """
    Check if a user has premium status.

    Queries the PremiumUser table to determine if the user has
    completed payment and has an active premium subscription.

    Args:
        session: Database session
        user_id: The user's UUID

    Returns:
        True if user has an active premium subscription
    """
    logger.debug(f"Checking premium status for user {user_id}")

    premium_user = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == user_id)
    ).first()

    is_premium = premium_user is not None and premium_user.is_premium
    logger.debug(f"User {user_id} premium status: {is_premium}")

    return is_premium


def can_user_create_item(session: Session, user: User) -> bool:
    """
    Check if user can create a new item based on their tier.

    Superusers and premium users can always create items.
    Free users are limited to FREE_TIER_ITEM_LIMIT items.

    Args:
        session: Database session
        user: The current user

    Returns:
        True if user can create another item
    """
    if user.is_superuser:
        logger.debug(f"User {user.id} is superuser, bypassing limit")
        return True

    if is_user_premium(session, user.id):
        logger.debug(f"User {user.id} is premium, no limit")
        return True

    item_count = session.exec(
        select(func.count()).select_from(Item).where(Item.owner_id == user.id)
    ).one()

    can_create = item_count < FREE_TIER_ITEM_LIMIT
    logger.debug(f"User {user.id} has {item_count} items, can_create={can_create}")

    return can_create
