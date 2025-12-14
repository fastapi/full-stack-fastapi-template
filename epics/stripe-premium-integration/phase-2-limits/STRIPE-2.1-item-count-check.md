# STRIPE-2.1: Add Item Count Check

## Status: COMPLETE

## Summary
Modify the `POST /api/v1/items` endpoint to enforce item limits for free users. Free users can create up to 2 items, premium users have no limit. Use a helper function for reusability.

## Acceptance Criteria
- [ ] Free users can create up to 2 items
- [ ] Free users get 403 error when trying to create 3rd item
- [ ] Premium users can create unlimited items
- [ ] Superusers bypass the limit check
- [ ] Error response includes clear message about upgrade
- [ ] Helper function created for checking premium status

## Technical Details

### Helper Function
Create `backend/app/premium_users/service.py`:
```python
"""
Premium user service functions.

Provides helper functions for checking premium status and enforcing
feature limits throughout the application.
"""

import logging

from sqlmodel import Session, func, select

from app.models import Item, User
from app.premium_users.models import PremiumUser

logger = logging.getLogger(__name__)

FREE_TIER_ITEM_LIMIT = 2


def is_user_premium(session: Session, user_id: uuid.UUID) -> bool:
    """
    Check if a user has premium status.

    Args:
        session: Database session
        user_id: The user's UUID

    Returns:
        True if user has an active premium subscription
    """
    premium_user = session.exec(
        select(PremiumUser).where(PremiumUser.user_id == user_id)
    ).first()

    return premium_user is not None and premium_user.is_premium


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
        return True

    if is_user_premium(session, user.id):
        return True

    item_count = session.exec(
        select(func.count())
        .select_from(Item)
        .where(Item.owner_id == user.id)
    ).one()

    return item_count < FREE_TIER_ITEM_LIMIT


```

### Update items.py
```python
from fastapi import status
from app.premium_users.service import can_user_create_item, FREE_TIER_ITEM_LIMIT

@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.

    Free users limited to 2 items. Premium users have no limit.
    """
    if not can_user_create_item(session, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Free tier limited to {FREE_TIER_ITEM_LIMIT} items. Upgrade to premium for unlimited items.",
        )

    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
```

### Files to Create/Modify
1. `backend/app/premium_users/service.py` - NEW: Helper functions
2. `backend/app/api/routes/items.py` - Add limit check to create_item

## API Contract

### Error Response (403)
```json
{
  "detail": "Free tier limited to 2 items. Upgrade to premium for unlimited items."
}
```

## Dependencies
- STRIPE-1.1 (PremiumUser model must exist)

## Testing
- [ ] Free user with 0 items can create item (success)
- [ ] Free user with 1 item can create item (success)
- [ ] Free user with 2 items cannot create item (403)
- [ ] Premium user with 2+ items can create item (success)
- [ ] Superuser bypasses limit check
- [ ] Error message mentions upgrade
- [ ] `is_user_premium()` returns correct status
- [ ] `can_user_create_item()` returns correct boolean

## Notes
- Helper functions in service.py can be reused for other premium features
