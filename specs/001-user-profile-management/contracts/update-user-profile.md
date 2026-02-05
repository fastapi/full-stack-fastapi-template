# API Contract: Update User Profile

**Endpoint**: `PATCH /api/v1/users/me`  
**Method**: PATCH  
**Authentication**: Required (JWT Bearer token)  
**Feature**: User Profile Management

## Description

Updates the authenticated user's profile information. Supports partial updates - only provided fields are updated.

## Request

### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Path Parameters

None

### Query Parameters

None

### Request Body

**Content-Type**: `application/json`

**Schema**: `UserUpdateMe`

```json
{
  "email": "newemail@example.com",
  "full_name": "Jane Doe"
}
```

**Fields** (all optional):
- `email` (string, optional): New email address (must be valid format, unique)
- `full_name` (string, optional): New full name (max 255 characters, can be null/empty)

**Partial Update Behavior**:
- Only fields present in request body are updated
- Omitted fields remain unchanged
- `null` values are accepted for `full_name` (clears the field)

## Response

### Success Response (200 OK)

**Content-Type**: `application/json`

**Schema**: `UserPublic` (updated user data)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Error Responses

#### 400 Bad Request

Validation error or invalid input.

**Email Format Invalid**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address"
    }
  ]
}
```

**Full Name Too Long**:
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "full_name"],
      "msg": "String should have at most 255 characters"
    }
  ]
}
```

#### 409 Conflict

Email address already exists for another user.

```json
{
  "detail": "User with this email already exists"
}
```

#### 401 Unauthorized

User is not authenticated or token is invalid.

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

User account is deactivated.

```json
{
  "detail": "User account is deactivated"
}
```

## Test Cases

### TC-PATCH-001: Successful Email Update

**Given**: User is authenticated  
**When**: PATCH request updates email to a new, unique email  
**Then**: Email is updated, response contains updated profile with status 200

### TC-PATCH-002: Successful Full Name Update

**Given**: User is authenticated  
**When**: PATCH request updates full_name  
**Then**: Full name is updated, response contains updated profile with status 200

### TC-PATCH-003: Partial Update (Email Only)

**Given**: User is authenticated  
**When**: PATCH request includes only email field  
**Then**: Only email is updated, full_name remains unchanged

### TC-PATCH-004: Partial Update (Full Name Only)

**Given**: User is authenticated  
**When**: PATCH request includes only full_name field  
**Then**: Only full_name is updated, email remains unchanged

### TC-PATCH-005: Clear Full Name (Set to Null)

**Given**: User has a full_name set  
**When**: PATCH request sets full_name to null  
**Then**: Full name is cleared, response shows null full_name

### TC-PATCH-006: Duplicate Email Error

**Given**: User is authenticated, another user has email "existing@example.com"  
**When**: PATCH request updates email to "existing@example.com"  
**Then**: Response is 409 Conflict with error message

### TC-PATCH-007: Invalid Email Format

**Given**: User is authenticated  
**When**: PATCH request includes invalid email format  
**Then**: Response is 400 Bad Request with validation error

### TC-PATCH-008: Full Name Too Long

**Given**: User is authenticated  
**When**: PATCH request includes full_name exceeding 255 characters  
**Then**: Response is 400 Bad Request with validation error

### TC-PATCH-009: Update to Same Email

**Given**: User's current email is "user@example.com"  
**When**: PATCH request updates email to "user@example.com"  
**Then**: Update succeeds (no-op) or shows message that no changes were made

### TC-PATCH-010: Empty Request Body

**Given**: User is authenticated  
**When**: PATCH request has empty body  
**Then**: No fields are updated, response returns current profile data

### TC-PATCH-011: Unauthenticated Request

**Given**: User is not authenticated  
**When**: PATCH request is made without Authorization header  
**Then**: Response is 401 Unauthorized

## Implementation Notes

- Endpoint uses `CurrentUser` dependency for authentication
- Email uniqueness check compares against all users except current user
- Uses `model_dump(exclude_unset=True)` to support partial updates
- Updates are committed immediately (no transaction rollback needed for this feature)
- Response time target: < 30 seconds for complete update flow (per SC-002)
- Success rate target: 95% of updates succeed on first try (per SC-003)
