# Data Model: User Profile Management

**Feature**: User Profile Management  
**Date**: 2025-01-27  
**Phase**: 1 - Design & Contracts

## Entities

### User Profile

Represents a user's account information that can be viewed and updated through the profile management interface.

**Database Table**: `user` (existing)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Read-only | Unique identifier for the user (system-generated) |
| `email` | EmailStr | Required, Unique, Max 255 chars | User's email address (validated format) |
| `full_name` | String | Optional, Max 255 chars | User's display name (can be null/empty) |
| `is_active` | Boolean | Read-only | Account activation status |
| `is_superuser` | Boolean | Read-only | Superuser privilege flag |
| `created_at` | DateTime | Read-only | Account creation timestamp |
| `hashed_password` | String | Read-only | Password hash (not exposed in profile) |

**Relationships**:
- User has many Items (one-to-many, via `items` relationship)
- No new relationships introduced by this feature

**Validation Rules**:

1. **Email**:
   - Must be valid email format (validated by Pydantic `EmailStr`)
   - Must be unique across all users
   - Maximum length: 255 characters
   - Required field (cannot be null)

2. **Full Name**:
   - Optional field (can be null or empty string)
   - Maximum length: 255 characters
   - No minimum length requirement
   - Accepts any printable characters

**State Transitions**:

- **View State**: User profile is displayed in read-only mode
- **Edit State**: User profile fields become editable
- **Saving State**: Profile update request is in progress
- **Success State**: Profile update completed successfully
- **Error State**: Profile update failed (validation error, server error, network error)

**Business Rules**:

1. Users can only view and update their own profile (enforced by authentication)
2. Email uniqueness is enforced at the database level and validated on update
3. Partial updates are supported - only changed fields are sent to the API
4. Profile updates are immediate - no approval workflow
5. No audit trail required for profile updates (per specification scope)

## API Models

### UserPublic (Response Model)

Used for returning user profile data in API responses.

```python
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
```

**Fields Exposed**: `id`, `email`, `full_name`, `is_active`, `is_superuser`, `created_at`

### UserUpdateMe (Request Model)

Used for updating user's own profile.

```python
class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
```

**Validation**:
- Both fields are optional
- Email must be valid format if provided
- Full name max 255 characters if provided
- Email uniqueness checked if email is being updated

## Database Schema

No database schema changes required. Existing `user` table already supports all required fields:

- `id` (UUID, primary key)
- `email` (VARCHAR(255), unique, indexed)
- `full_name` (VARCHAR(255), nullable)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- Other fields (is_active, is_superuser, hashed_password) are read-only for this feature

## Data Flow

1. **Profile View**:
   - User requests profile → `GET /users/me` → Returns `UserPublic` → Displayed in UI

2. **Profile Update**:
   - User edits fields → Frontend validates → `PATCH /users/me` with `UserUpdateMe` → Backend validates → Database update → Returns updated `UserPublic` → UI refreshes

3. **Error Handling**:
   - Validation error → Error message displayed → User can retry
   - Duplicate email → 409 Conflict → Specific error message displayed
   - Network error → Error message displayed → User can retry

## Notes

- No new database migrations needed
- Existing models are sufficient
- No new relationships or foreign keys
- All data operations are on existing `user` table
