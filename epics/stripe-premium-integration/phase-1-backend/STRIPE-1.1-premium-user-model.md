# STRIPE-1.1: Create PremiumUser Model and Migration

## Summary
Create a new `PremiumUser` database model to store Stripe payment and premium status data, with a one-to-one relationship to the User table.

## Acceptance Criteria
- [ ] PremiumUser model exists in `backend/app/models.py`
- [ ] All required fields are present with correct types
- [ ] Foreign key relationship to User table is configured
- [ ] Alembic migration is created and runs successfully
- [ ] Migration can be rolled back (downgrade works)
- [ ] Model is exported from models module

## Technical Details

### Model Definition
```python
class PremiumUser(SQLModel, table=True):
    """
    Stores Stripe payment and premium status data.
    One-to-one relationship with User.

    Created when a user completes Stripe checkout.
    Used to check premium status for feature gating.
    """
    premium_user_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    stripe_customer_id: str = Field(index=True)  # Stripe's customer ID (cus_xxx)
    is_premium: bool = Field(default=False)  # Premium status flag
    payment_intent_id: str | None = Field(default=None)  # Stripe payment intent (pi_xxx)
    paid_at: datetime | None = Field(default=None)  # When payment completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Constraints
- `user_id`: UNIQUE constraint (one premium record per user)
- `user_id`: INDEX for fast lookups
- `stripe_customer_id`: INDEX for webhook lookups

### Files to Modify
1. `backend/app/models.py` - Add PremiumUser class
2. Run: `alembic revision --autogenerate -m "Add PremiumUser table"`
3. Review generated migration in `backend/app/alembic/versions/`
4. Run: `alembic upgrade head`

### Migration Commands
```bash
# Inside backend container
docker compose exec backend bash

# Generate migration
alembic revision --autogenerate -m "Add PremiumUser table"

# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

## Dependencies
- None (first ticket in phase)

## Testing
- [ ] Migration applies without errors
- [ ] Migration rollback works
- [ ] Can create PremiumUser record via Python shell
- [ ] Unique constraint prevents duplicate user_id
- [ ] Foreign key prevents invalid user_id

## Notes
- Do NOT add relationship to User model yet (keep it simple)
- Premium status checked via JOIN when needed
- stripe_customer_id comes from Stripe API response
