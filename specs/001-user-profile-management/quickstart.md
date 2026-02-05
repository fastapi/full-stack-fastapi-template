# Quickstart: User Profile Management

**Feature**: User Profile Management  
**Date**: 2025-01-27  
**Phase**: 1 - Design & Contracts

## Integration Scenarios

### Scenario 1: View User Profile

**Objective**: Display user's current profile information

**Steps**:
1. User navigates to Settings page (`/settings`)
2. User clicks on "My profile" tab (default tab)
3. Frontend calls `GET /api/v1/users/me` with JWT token
4. Backend returns `UserPublic` with user's email and full_name
5. Frontend displays profile information in view mode

**Expected Result**: User sees their current email and full name displayed

**Test Command**:
```bash
curl -X GET "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json"
```

**Expected Response**:
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

### Scenario 2: Update Email Address

**Objective**: User updates their email address

**Steps**:
1. User views profile (see Scenario 1)
2. User clicks "Edit" button
3. Frontend switches to edit mode
4. User changes email field to "newemail@example.com"
5. User clicks "Save"
6. Frontend validates email format client-side
7. Frontend calls `PATCH /api/v1/users/me` with `{"email": "newemail@example.com"}`
8. Backend validates email format and uniqueness
9. Backend updates user record
10. Backend returns updated `UserPublic`
11. Frontend displays success message
12. Frontend switches back to view mode
13. Frontend displays updated email

**Expected Result**: Email is updated, user sees success message and updated email

**Test Command**:
```bash
curl -X PATCH "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@example.com"}'
```

**Expected Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Scenario 3: Update Full Name

**Objective**: User updates their full name

**Steps**:
1. User views profile
2. User clicks "Edit" button
3. User changes full_name field to "Jane Smith"
4. User clicks "Save"
5. Frontend validates full_name length (max 255 chars) client-side
6. Frontend calls `PATCH /api/v1/users/me` with `{"full_name": "Jane Smith"}`
7. Backend validates full_name length
8. Backend updates user record
9. Backend returns updated `UserPublic`
10. Frontend displays success message and updated name

**Expected Result**: Full name is updated, user sees success message

**Test Command**:
```bash
curl -X PATCH "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Smith"}'
```

### Scenario 4: Update Both Fields

**Objective**: User updates both email and full name simultaneously

**Steps**:
1. User enters edit mode
2. User changes both email and full_name
3. User clicks "Save"
4. Frontend validates both fields
5. Frontend calls `PATCH /api/v1/users/me` with both fields
6. Backend validates and updates both fields
7. Backend returns updated profile

**Expected Result**: Both fields are updated successfully

**Test Command**:
```bash
curl -X PATCH "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "updated@example.com", "full_name": "Updated Name"}'
```

### Scenario 5: Cancel Edit

**Objective**: User cancels profile edit without saving

**Steps**:
1. User enters edit mode
2. User makes changes to fields
3. User clicks "Cancel" button
4. Frontend resets form to original values
5. Frontend switches back to view mode
6. No API call is made

**Expected Result**: Changes are discarded, profile returns to original state

### Scenario 6: Validation Error - Invalid Email

**Objective**: System prevents invalid email format

**Steps**:
1. User enters edit mode
2. User enters invalid email "not-an-email"
3. User clicks "Save"
4. Frontend validates and shows error immediately (client-side)
5. OR if client-side validation passes, backend validates
6. Backend returns 400 Bad Request with validation error
7. Frontend displays error message

**Expected Result**: Update is prevented, user sees validation error

**Test Command**:
```bash
curl -X PATCH "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email"}'
```

**Expected Response**: 400 Bad Request

### Scenario 7: Validation Error - Duplicate Email

**Objective**: System prevents duplicate email addresses

**Steps**:
1. Another user exists with email "existing@example.com"
2. Current user tries to update email to "existing@example.com"
3. User clicks "Save"
4. Frontend calls `PATCH /api/v1/users/me`
5. Backend checks email uniqueness
6. Backend returns 409 Conflict
7. Frontend displays error message indicating email is already in use

**Expected Result**: Update is prevented, user sees duplicate email error

**Test Command**:
```bash
curl -X PATCH "http://localhost/api/v1/users/me" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "existing@example.com"}'
```

**Expected Response**: 409 Conflict

### Scenario 8: Validation Error - Full Name Too Long

**Objective**: System prevents full name exceeding 255 characters

**Steps**:
1. User enters edit mode
2. User enters full_name with 256+ characters
3. User clicks "Save"
4. Frontend validates length and shows error (client-side)
5. OR backend validates and returns 400 Bad Request
6. Frontend displays error message

**Expected Result**: Update is prevented, user sees length validation error

### Scenario 9: Network Error Handling

**Objective**: System handles network failures gracefully

**Steps**:
1. User makes profile update
2. Network request fails (timeout, connection error)
3. Frontend detects network error
4. Frontend displays error message
5. User can retry the update

**Expected Result**: User sees error message, can retry without data loss

### Scenario 10: Unauthenticated Access

**Objective**: System prevents unauthenticated profile access

**Steps**:
1. User is not logged in
2. User navigates to `/settings`
3. Frontend redirects to login page
4. OR if API is called directly, backend returns 401 Unauthorized

**Expected Result**: User is redirected to login or sees authentication error

## Testing Checklist

- [ ] Profile view displays correctly
- [ ] Edit mode toggles correctly
- [ ] Email update succeeds
- [ ] Full name update succeeds
- [ ] Both fields update together
- [ ] Cancel discards changes
- [ ] Invalid email is rejected
- [ ] Duplicate email is rejected
- [ ] Full name length validation works
- [ ] Network errors are handled
- [ ] Unauthenticated access is prevented
- [ ] Success messages display
- [ ] Error messages display
- [ ] Form resets properly on cancel
- [ ] Partial updates work correctly
