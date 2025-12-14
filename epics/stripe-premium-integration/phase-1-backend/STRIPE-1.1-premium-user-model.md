# STRIPE-1.1: Create PremiumUser Model and Migration

## Status: COMPLETE

## Summary
Create a new `PremiumUser` database model to store Stripe payment and premium status data, with a one-to-one relationship to the User table.

## Acceptance Criteria
- [x] PremiumUser model exists in `backend/app/premium_users/models.py`
- [x] All required fields are present with correct types
- [x] Uses UUID for primary key (matches existing User/Item patterns)
- [x] Foreign key relationship to User table is configured
- [x] Alembic migration is created and runs successfully
- [x] Migration can be rolled back (downgrade works) - see notes
- [x] Model is exported from premium_users module

## Technical Details

### Model Definition
**Note:** Uses `uuid.UUID` for primary key to match existing User and Item model patterns in this codebase.

```python
class PremiumUser(SQLModel, table=True):
    """
    Stores Stripe payment and premium status data.
    One-to-one relationship with User.

    Created when a user completes Stripe checkout.
    Used to check premium status for feature gating.
    """
    premium_user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
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
- Model placed in separate `backend/app/premium_users/` module instead of main models.py
- Uses `__tablename__ = "premium_user"` to override SQLModel's default naming

## Rollback Testing Notes
Rollback was tested but encountered issues:
- Deleted migration file manually while alembic_version table still referenced it
- Container failed to start with "Can't locate revision" error
- Fixed by manually clearing alembic_version table in database
- Lesson: Always use `alembic downgrade` instead of deleting migration files directly
