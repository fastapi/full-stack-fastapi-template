---
title: "Test Registry"
doc-type: reference
status: draft
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - "backend/tests/**/*.py"
  - "frontend/tests/**/*.spec.ts"
related-docs:
  - docs/testing/strategy.md
tags: [testing, quality, registry]
---

# Test Registry

## Coverage Summary

| Module | Unit | Integration | E2E | Total |
|--------|------|-------------|-----|-------|
| backend/api/routes | 0 | 47 | 0 | 47 |
| backend/crud | 10 | 0 | 0 | 10 |
| backend/scripts | 2 | 0 | 0 | 2 |
| frontend/login | 0 | 0 | 9 | 9 |
| frontend/admin | 0 | 0 | 12 | 12 |
| frontend/items | 0 | 0 | 9 | 9 |
| frontend/user-settings | 0 | 0 | 14 | 14 |
| frontend/sign-up | 0 | 0 | 11 | 11 |
| frontend/reset-password | 0 | 0 | 6 | 6 |
| **Total** | **12** | **47** | **61** | **120** |

## Test Inventory

### Backend — API Routes: Items (`backend/tests/api/routes/test_items.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_create_item | Creates item with valid title and description | integration | passing |
| test_read_item | Retrieves item by ID as superuser | integration | passing |
| test_read_item_not_found | Returns 404 for non-existent item | integration | passing |
| test_read_item_not_enough_permissions | Rejects item read without ownership | integration | passing |
| test_read_items | Lists items with pagination support | integration | passing |
| test_update_item | Updates item title and description | integration | passing |
| test_update_item_not_found | Returns 404 when updating non-existent item | integration | passing |
| test_update_item_not_enough_permissions | Rejects item update without ownership | integration | passing |
| test_delete_item | Deletes item as superuser | integration | passing |
| test_delete_item_not_found | Returns 404 when deleting non-existent item | integration | passing |
| test_delete_item_not_enough_permissions | Rejects item deletion without ownership | integration | passing |

### Backend — API Routes: Login (`backend/tests/api/routes/test_login.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_get_access_token | Authenticates superuser with valid credentials | integration | passing |
| test_get_access_token_incorrect_password | Rejects login with wrong password | integration | passing |
| test_use_access_token | Validates access token via test-token endpoint | integration | passing |
| test_recovery_password | Sends password recovery email for existing user | integration | passing |
| test_recovery_password_user_not_exits | Returns generic message for non-existent email | integration | passing |
| test_reset_password | Resets password with valid token | integration | passing |
| test_reset_password_invalid_token | Rejects password reset with invalid token | integration | passing |
| test_login_with_bcrypt_password_upgrades_to_argon2 | Upgrades bcrypt hash to argon2 on login | integration | passing |
| test_login_with_argon2_password_keeps_hash | Preserves argon2 hash without re-hashing | integration | passing |

### Backend — API Routes: Users (`backend/tests/api/routes/test_users.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_get_users_superuser_me | Returns superuser profile via /me endpoint | integration | passing |
| test_get_users_normal_user_me | Returns normal user profile via /me endpoint | integration | passing |
| test_create_user_new_email | Creates user with unique email as superuser | integration | passing |
| test_get_existing_user_as_superuser | Retrieves user by ID as superuser | integration | passing |
| test_get_non_existing_user_as_superuser | Returns 404 for non-existent user ID | integration | passing |
| test_get_existing_user_current_user | Retrieves own profile by ID | integration | passing |
| test_get_existing_user_permissions_error | Rejects reading other user without superuser role | integration | passing |
| test_get_non_existing_user_permissions_error | Returns 403 for non-superuser accessing others | integration | passing |
| test_create_user_existing_username | Rejects duplicate email registration | integration | passing |
| test_create_user_by_normal_user | Rejects user creation by non-superuser | integration | passing |
| test_retrieve_users | Lists all users as superuser | integration | passing |
| test_update_user_me | Updates own name and email | integration | passing |
| test_update_password_me | Changes own password with valid current password | integration | passing |
| test_update_password_me_incorrect_password | Rejects password change with wrong current password | integration | passing |
| test_update_user_me_email_exists | Rejects email update to existing email | integration | passing |
| test_update_password_me_same_password_error | Rejects changing to same password | integration | passing |
| test_register_user | Registers new user via signup endpoint | integration | passing |
| test_register_user_already_exists_error | Rejects signup with existing email | integration | passing |
| test_update_user | Updates user as superuser | integration | passing |
| test_update_user_not_exists | Returns 404 when updating non-existent user | integration | passing |
| test_update_user_email_exists | Rejects updating user email to existing email | integration | passing |
| test_delete_user_me | Deletes own account as normal user | integration | passing |
| test_delete_user_me_as_superuser | Rejects self-deletion by superuser | integration | passing |
| test_delete_user_super_user | Deletes another user as superuser | integration | passing |
| test_delete_user_not_found | Returns 404 when deleting non-existent user | integration | passing |
| test_delete_user_current_super_user_error | Rejects superuser deleting themselves by ID | integration | passing |
| test_delete_user_without_privileges | Rejects deletion by non-superuser | integration | passing |

### Backend — API Routes: Private (`backend/tests/api/routes/test_private.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_create_user | Creates user via private API without auth | integration | passing |

### Backend — CRUD: User (`backend/tests/crud/test_user.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_create_user | Creates user and verifies hashed password exists | unit | passing |
| test_authenticate_user | Authenticates user with correct credentials | unit | passing |
| test_not_authenticate_user | Rejects authentication with non-existent email | unit | passing |
| test_check_if_user_is_active | Verifies new user defaults to active | unit | passing |
| test_check_if_user_is_active_inactive | Creates inactive user and verifies status | unit | passing |
| test_check_if_user_is_superuser | Creates superuser and verifies flag | unit | passing |
| test_check_if_user_is_superuser_normal_user | Verifies normal user is not superuser | unit | passing |
| test_get_user | Retrieves user by ID and compares fields | unit | passing |
| test_update_user | Updates user password and verifies new hash | unit | passing |
| test_authenticate_user_with_bcrypt_upgrades_to_argon2 | Upgrades bcrypt password hash to argon2 on auth | unit | passing |

### Backend — Scripts (`backend/tests/scripts/`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_init_successful_connection (backend_pre_start) | Verifies backend pre-start DB connection | unit | passing |
| test_init_successful_connection (test_pre_start) | Verifies test pre-start DB connection | unit | passing |

### Frontend — Login (`frontend/tests/login.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| Inputs are visible, empty and editable | Validates login form inputs are present | e2e | passing |
| Log In button is visible | Checks login button renders | e2e | passing |
| Forgot Password link is visible | Checks password recovery link renders | e2e | passing |
| Log in with valid email and password | Authenticates with valid credentials | e2e | passing |
| Log in with invalid email | Shows validation error for invalid email | e2e | passing |
| Log in with invalid password | Shows error for incorrect password | e2e | passing |
| Successful log out | Logs in then logs out successfully | e2e | passing |
| Logged-out user cannot access protected routes | Redirects to login after logout | e2e | passing |
| Redirects to /login when token is wrong | Handles invalid token in localStorage | e2e | passing |

### Frontend — Admin (`frontend/tests/admin.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| Admin page is accessible and shows correct title | Validates admin page heading renders | e2e | passing |
| Add User button is visible | Checks add user button renders | e2e | passing |
| Create a new user successfully | Creates user via admin form | e2e | passing |
| Create a superuser | Creates superuser with admin privileges | e2e | passing |
| Edit a user successfully | Edits user name via admin actions | e2e | passing |
| Delete a user successfully | Deletes user via admin actions | e2e | passing |
| Cancel user creation | Cancels add user dialog | e2e | passing |
| Email is required and must be valid | Shows validation for invalid email | e2e | passing |
| Password must be at least 8 characters | Shows validation for weak password | e2e | passing |
| Passwords must match | Shows mismatch error for passwords | e2e | passing |
| Non-superuser cannot access admin page | Restricts admin access for normal users | e2e | passing |
| Superuser can access admin page | Grants admin access for superusers | e2e | passing |

### Frontend — Items (`frontend/tests/items.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| Items page is accessible and shows correct title | Validates items page heading renders | e2e | passing |
| Add Item button is visible | Checks add item button renders | e2e | passing |
| Create a new item successfully | Creates item with title and description | e2e | passing |
| Create item with only required fields | Creates item with title only | e2e | passing |
| Cancel item creation | Cancels add item dialog | e2e | passing |
| Title is required | Shows validation for empty title | e2e | passing |
| Edit an item successfully | Edits item title via actions menu | e2e | passing |
| Delete an item successfully | Deletes item via actions menu | e2e | passing |
| Shows empty state message when no items exist | Displays empty state for new user | e2e | passing |

### Frontend — User Settings (`frontend/tests/user-settings.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| My profile tab is active by default | Validates default tab selection | e2e | passing |
| All tabs are visible | Checks all settings tabs render | e2e | passing |
| Edit user name with a valid name | Updates user full name | e2e | passing |
| Edit user email with an invalid email shows error | Shows validation for invalid email | e2e | passing |
| Edit user email with a valid email | Updates user email address | e2e | passing |
| Cancel edit action restores original name | Reverts name on cancel | e2e | passing |
| Cancel edit action restores original email | Reverts email on cancel | e2e | passing |
| Update password successfully | Changes password and re-authenticates | e2e | passing |
| Update password with weak passwords | Shows validation for weak password | e2e | passing |
| New password and confirmation password do not match | Shows password mismatch error | e2e | passing |
| Current password and new password are the same | Rejects reusing current password | e2e | passing |
| Appearance button is visible in sidebar | Checks theme toggle renders | e2e | passing |
| User can switch between theme modes | Toggles dark/light themes | e2e | passing |
| Selected mode is preserved across sessions | Persists theme across logout/login | e2e | passing |

### Frontend — Sign Up (`frontend/tests/sign-up.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| Inputs are visible, empty and editable | Validates signup form inputs are present | e2e | passing |
| Sign Up button is visible | Checks signup button renders | e2e | passing |
| Log In link is visible | Checks login link renders | e2e | passing |
| Sign up with valid name, email, and password | Registers new user successfully | e2e | passing |
| Sign up with invalid email | Shows validation for invalid email | e2e | passing |
| Sign up with existing email | Shows error for duplicate email | e2e | passing |
| Sign up with weak password | Shows validation for weak password | e2e | passing |
| Sign up with mismatched passwords | Shows password mismatch error | e2e | passing |
| Sign up with missing full name | Shows validation for empty name | e2e | passing |
| Sign up with missing email | Shows validation for empty email | e2e | passing |
| Sign up with missing password | Shows validation for empty password | e2e | passing |

### Frontend — Reset Password (`frontend/tests/reset-password.spec.ts`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| Password Recovery title is visible | Validates recovery page heading | e2e | passing |
| Input is visible, empty and editable | Checks email input renders | e2e | passing |
| Continue button is visible | Checks continue button renders | e2e | passing |
| User can reset password successfully using the link | Completes full password reset flow | e2e | passing |
| Expired or invalid reset link | Shows error for invalid reset token | e2e | passing |
| Weak new password validation | Shows validation for weak new password | e2e | passing |

## Coverage Gaps

| Module | Gap | Linked Issue |
|--------|-----|-------------|
| backend/core/security | No unit tests for password hashing and JWT creation | - |
| backend/core/config | No unit tests for settings validation and secret checks | - |
| backend/core/db | No unit tests for engine creation and init_db | - |
| backend/utils | No unit tests for email generation and token utilities | - |
| frontend | No unit or integration tests (Playwright E2E only) | - |
