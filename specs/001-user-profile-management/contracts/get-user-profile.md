# API Contract: Get User Profile

**Endpoint**: `GET /api/v1/users/me`
**Method**: GET
**Authentication**: Required (JWT Bearer token)
**Feature**: User Profile Management

## Description

Retrieves the authenticated user's profile information including email address and full name.

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

None

## Response

### Success Response (200 OK)

**Content-Type**: `application/json`

**Schema**: `UserPublic`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Fields**:
- `id` (UUID, required): User's unique identifier
- `email` (string, required): User's email address
- `full_name` (string, optional): User's display name (can be null)
- `is_active` (boolean, required): Account activation status
- `is_superuser` (boolean, required): Superuser privilege flag
- `created_at` (datetime, optional): Account creation timestamp

### Error Responses

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

### TC-GET-001: Successful Profile Retrieval

**Given**: User is authenticated
**When**: GET request is made to `/api/v1/users/me`
**Then**: Response contains user's profile data with status 200

### TC-GET-002: Unauthenticated Request

**Given**: User is not authenticated
**When**: GET request is made without Authorization header
**Then**: Response is 401 Unauthorized

### TC-GET-003: Profile with Null Full Name

**Given**: User has null full_name
**When**: GET request retrieves profile
**Then**: Response contains `full_name: null` or field is omitted

## Implementation Notes

- Endpoint uses `CurrentUser` dependency for authentication
- Returns `UserPublic` model which excludes sensitive fields (hashed_password)
- No caching required - always returns current data
- Response time target: < 2 seconds (per SC-001)
