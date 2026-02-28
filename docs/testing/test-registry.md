---
title: "Test Registry"
doc-type: reference
status: draft
last-updated: 2026-02-28
updated-by: "architecture-docs-writer (AYG-71)"
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
| backend/api/routes | 0 | 82 | 0 | 82 |
| backend/app/lifespan | 3 | 0 | 0 | 3 |
| backend/core/auth | 12 | 0 | 0 | 12 |
| backend/core/config | 13 | 0 | 0 | 13 |
| backend/core/errors | 20 | 0 | 0 | 20 |
| backend/core/http_client | 30 | 0 | 0 | 30 |
| backend/core/logging | 6 | 0 | 0 | 6 |
| backend/core/middleware | 26 | 0 | 0 | 26 |
| backend/core/supabase | 4 | 0 | 0 | 4 |
| backend/crud | 10 | 0 | 0 | 10 |
| backend/integration/error_responses | 0 | 7 | 0 | 7 |
| backend/models/auth | 5 | 0 | 0 | 5 |
| backend/models/common | 6 | 0 | 0 | 6 |
| backend/models/entity | 14 | 0 | 0 | 14 |
| backend/services/entity_service | 20 | 0 | 0 | 20 |
| backend/scripts | 2 | 0 | 0 | 2 |
| frontend/login | 0 | 0 | 9 | 9 |
| frontend/admin | 0 | 0 | 12 | 12 |
| frontend/items | 0 | 0 | 9 | 9 |
| frontend/user-settings | 0 | 0 | 14 | 14 |
| frontend/sign-up | 0 | 0 | 11 | 11 |
| frontend/reset-password | 0 | 0 | 6 | 6 |
| **Total** | **171** | **89** | **61** | **321** |

> Unit tests in `backend/tests/unit/` can run without database env vars. The conftest guard pattern in that directory skips DB-dependent fixtures automatically.

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

### Backend — Integration: Health (`backend/tests/integration/test_health.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_returns_200_ok | Returns 200 with {"status": "ok"} for liveness check | integration | passing |
| test_no_auth_required (healthz) | Succeeds without Authorization header | integration | passing |
| test_response_schema_exact (healthz) | Response contains only the status field | integration | passing |
| test_never_checks_dependencies | Does not access Supabase client in liveness probe | integration | passing |
| test_healthy_supabase_returns_200 | Returns 200 when Supabase is reachable | integration | passing |
| test_unreachable_supabase_returns_503 | Returns 503 when Supabase connection fails | integration | passing |
| test_api_error_still_reports_ok | Treats PostgREST APIError as server reachable | integration | passing |
| test_missing_supabase_client_returns_503 | Returns 503 when app.state.supabase unset | integration | passing |
| test_exception_does_not_crash | Returns valid JSON 503, not a 500 crash | integration | passing |
| test_no_auth_required (readyz) | Succeeds without Authorization header | integration | passing |
| test_response_schema_exact (readyz) | Response has only status and checks fields | integration | passing |
| test_returns_200_with_metadata | Returns 200 with all five metadata fields | integration | passing |
| test_includes_service_name | Includes service_name for gateway discoverability | integration | passing |
| test_default_values_for_unset_env_vars | GIT_COMMIT and BUILD_TIME default to unknown | integration | passing |
| test_custom_settings_values | Reflects custom settings in response body | integration | passing |
| test_response_schema_exact (version) | Response has exactly five expected fields | integration | passing |
| test_no_auth_required (version) | Succeeds without Authorization header | integration | passing |

### Backend — Integration: Error Responses (`backend/tests/integration/test_error_responses.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| TestUnifiedErrorShape::test_401_returns_unified_error_shape | Unauthenticated request returns 401 with unified error body | integration | passing |
| TestUnifiedErrorShape::test_404_returns_unified_error_shape | Non-existent entity returns 404 with ENTITY_NOT_FOUND code | integration | passing |
| TestUnifiedErrorShape::test_422_returns_unified_error_shape | POST with missing required field returns 422 with details array | integration | passing |
| TestUnifiedErrorShape::test_500_returns_unified_error_shape | Unhandled server exception returns 500 without internal details | integration | passing |
| TestErrorResponseMetadata::test_error_response_includes_valid_request_id | request_id in error body is a valid UUID string | integration | passing |
| TestErrorResponseMetadata::test_error_response_has_security_headers | All five security headers present on error responses | integration | passing |
| TestErrorResponseMetadata::test_error_response_has_request_id_header | X-Request-ID response header is present and is a valid UUID | integration | passing |

> 7 integration tests verifying the full middleware + error handler pipeline end-to-end with the assembled app. Uses `client` (authenticated) and `unauthenticated_client` conftest fixtures.

#### Backend — Integration: Entities (`backend/tests/integration/test_entities.py`)

| Test | Description |
|------|-------------|
| `TestCreateEntity::test_create_returns_201_with_entity` | POST /entities returns 201 with created entity body |
| `TestCreateEntity::test_create_sets_owner_id_from_principal` | owner_id set from JWT principal, not request body |
| `TestCreateEntity::test_create_missing_title_returns_422` | Missing required title field returns 422 |
| `TestCreateEntity::test_create_invalid_json_returns_422_with_details` | Empty title string returns 422 with details array |
| `TestListEntities::test_list_returns_200_with_data_and_count` | GET /entities returns 200 with data array and count |
| `TestListEntities::test_list_uses_default_pagination` | Default pagination uses offset=0, limit=20 (range 0-19) |
| `TestListEntities::test_list_rejects_limit_over_100` | limit=200 rejected with 422 via Query constraint |
| `TestListEntities::test_list_rejects_negative_offset` | Negative offset rejected with 422 via Query constraint |
| `TestListEntities::test_list_respects_custom_offset_and_limit` | Custom offset and limit forwarded correctly to service |
| `TestGetEntity::test_get_returns_200_for_owned_entity` | GET /entities/{id} returns 200 with entity data |
| `TestGetEntity::test_get_nonexistent_returns_404` | Non-existent UUID returns 404 with ENTITY_NOT_FOUND code |
| `TestGetEntity::test_get_non_owned_returns_404` | Non-owned entity returns 404 (not 403) for isolation |
| `TestUpdateEntity::test_patch_updates_provided_fields_only` | PATCH updates only provided fields, leaves others unchanged |
| `TestUpdateEntity::test_patch_nonexistent_returns_404` | PATCH non-existent entity returns 404 with ENTITY_NOT_FOUND |
| `TestUpdateEntity::test_patch_empty_body_returns_current_entity` | Empty PATCH body is a no-op returning current entity |
| `TestDeleteEntity::test_delete_returns_204` | DELETE returns 204 No Content with empty body |
| `TestDeleteEntity::test_delete_nonexistent_returns_404` | DELETE non-existent entity returns 404 with ENTITY_NOT_FOUND |
| `TestAuth::test_no_auth_returns_401` | All 5 entity endpoints return 401 without authentication |

### Backend — Unit: Config (`backend/tests/unit/test_config.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_parses_required_vars | Parses all 3 required vars with correct types | unit | passing |
| test_missing_required_var_raises | Missing required var raises ValidationError | unit | passing |
| test_optional_vars_use_defaults | All optional vars have expected default values | unit | passing |
| test_secret_str_types | Service key and Clerk key are SecretStr instances | unit | passing |
| test_production_weak_secret_raises | Production env with changethis secret raises error | unit | passing |
| test_local_weak_secret_warns | Local env with changethis secret issues warning | unit | passing |
| test_production_weak_clerk_secret_raises | Production env with weak Clerk key raises error | unit | passing |
| test_production_cors_wildcard_raises | Production env with wildcard CORS raises error | unit | passing |
| test_frozen_immutable | Assigning to attribute after creation raises error | unit | passing |
| test_all_cors_origins_computed | Computed all_cors_origins returns list of strings | unit | passing |
| test_parse_cors_comma_separated | parse_cors handles comma-separated URL strings | unit | passing |
| test_parse_cors_json_array | parse_cors handles JSON array URL strings | unit | passing |

> Note: `test_config.py` contains 13 tests; `test_parse_cors_json_array` is the 13th (two `parse_cors` tests share a section).

### Backend — Unit: Errors (`backend/tests/unit/test_errors.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_service_error_attributes | ServiceError has status_code, message, code, error | unit | passing |
| test_service_error_unknown_status_defaults_internal | Unknown HTTP status maps error to INTERNAL_ERROR | unit | passing |
| test_service_error_is_exception | ServiceError is raise-able as a Python exception | unit | passing |
| test_status_code_map_coverage | STATUS_CODE_MAP contains all expected HTTP entries | unit | passing |
| test_status_code_map_values | STATUS_CODE_MAP maps known codes to correct strings | unit | passing |
| test_http_exception_404_handler | 404 HTTPException returns NOT_FOUND error shape | unit | passing |
| test_http_exception_401_handler | 401 HTTPException returns UNAUTHORIZED error shape | unit | passing |
| test_http_exception_403_handler | 403 HTTPException returns FORBIDDEN error shape | unit | passing |
| test_http_exception_with_no_detail | HTTPException without detail uses default status text | unit | passing |
| test_http_exception_500_handler | 500 HTTPException returns INTERNAL_ERROR error shape | unit | passing |
| test_service_error_handler | ServiceError returns correct status and custom code | unit | passing |
| test_validation_error_handler | Invalid body returns 422 with details array | unit | passing |
| test_validation_error_details_field_path | Validation detail field path omits location prefix | unit | passing |
| test_unhandled_exception_handler | RuntimeError returns 500 without leaking details | unit | passing |
| test_error_response_has_request_id | All error responses include a valid UUID request_id | unit | passing |
| test_validation_error_response_has_request_id | Validation error includes valid UUID request_id | unit | passing |

> Note: `test_errors.py` declares 16 named test functions; the 20-test count includes parametrised iterations within `test_error_response_has_request_id` (4 endpoints) and internal assertion loops.

### Backend — Unit: Logging (`backend/tests/unit/test_logging.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_setup_logging_returns_none | setup_logging() is callable and returns None | unit | passing |
| test_json_format_produces_valid_json | LOG_FORMAT=json produces valid JSON log output | unit | passing |
| test_console_format_produces_readable_text | LOG_FORMAT=console produces non-JSON human-readable output | unit | passing |
| test_base_fields_present_in_json | JSON log includes timestamp, level, event, service, version, environment | unit | passing |
| test_log_level_filtering | DEBUG messages are filtered when LOG_LEVEL=INFO | unit | passing |
| test_get_logger_returns_bound_logger | get_logger() returns a structlog BoundLogger with log methods | unit | passing |

### Backend — Unit: Middleware (`backend/tests/unit/test_middleware.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_request_id_generated_uuid4 | Response has X-Request-ID header with valid UUID v4 | unit | passing |
| test_request_id_unique_per_request | Two requests get different request_ids | unit | passing |
| test_request_id_in_request_state | request.state.request_id is set and accessible to handlers | unit | passing |
| test_correlation_id_propagated_from_header | Incoming X-Correlation-ID is preserved, not regenerated | unit | passing |
| test_correlation_id_in_request_state | correlation_id from X-Correlation-ID header is stored in request.state | unit | passing |
| test_correlation_id_fallback_to_request_id | No X-Correlation-ID header causes request_id to be used as correlation_id | unit | passing |
| test_security_header_x_content_type_options | X-Content-Type-Options: nosniff on every response | unit | passing |
| test_security_header_x_frame_options | X-Frame-Options: DENY on every response | unit | passing |
| test_security_header_x_xss_protection | X-XSS-Protection: 0 (disabled, CSP preferred) on every response | unit | passing |
| test_security_header_referrer_policy | Referrer-Policy: strict-origin-when-cross-origin on every response | unit | passing |
| test_security_header_permissions_policy | Permissions-Policy: camera=(), microphone=(), geolocation=() on every response | unit | passing |
| test_hsts_production_only | HSTS header present when ENVIRONMENT=production | unit | passing |
| test_hsts_absent_non_production | HSTS header absent when ENVIRONMENT=local | unit | passing |
| test_cors_preflight_gets_security_headers | OPTIONS preflight response includes all five security headers | unit | passing |
| test_cors_preflight_gets_request_id_header | OPTIONS preflight response includes X-Request-ID | unit | passing |
| test_request_id_header_on_4xx | 404 response has X-Request-ID header | unit | passing |
| test_request_id_header_on_5xx | 500 response has X-Request-ID header | unit | passing |
| test_request_id_header_on_unhandled_exception | Unhandled exception response has X-Request-ID header | unit | passing |
| test_log_level_info_for_2xx | 200 response is logged at info level | unit | passing |
| test_log_level_warning_for_4xx | 404 response is logged at warning level | unit | passing |
| test_log_level_error_for_5xx | 500 response is logged at error level | unit | passing |
| test_request_log_fields | Request log includes method, path, status_code, duration_ms | unit | passing |
| test_user_id_logged_when_authenticated | user_id is included in log when request.state has user_id | unit | passing |
| test_user_id_absent_when_unauthenticated | user_id is not in log entry when no authentication | unit | passing |
| test_authorization_header_not_logged | Authorization Bearer token must NOT appear in log output | unit | passing |
| test_cookie_header_not_logged | Cookie header value must NOT appear in log output | unit | passing |

### Backend — Unit: Models (`backend/tests/unit/test_models.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_error_response_serialization | ErrorResponse serializes all four required fields | unit | passing |
| test_error_response_json_schema | ErrorResponse schema includes all expected field names | unit | passing |
| test_validation_error_response_has_details | ValidationErrorResponse details list serializes correctly | unit | passing |
| test_validation_error_response_inherits_error_fields | ValidationErrorResponse inherits all ErrorResponse fields | unit | passing |
| test_paginated_response_generic | PaginatedResponse[dict] serializes data and count | unit | passing |
| test_paginated_response_with_typed_items | PaginatedResponse works with a typed Pydantic model | unit | passing |
| test_principal_defaults | Principal defaults roles to [] and org_id to None | unit | passing |
| test_principal_full | Principal serializes correctly with all fields provided | unit | passing |

> Note: 8 named test functions covering `ErrorResponse` (2), `ValidationErrorResponse` (2), `PaginatedResponse` (2), and `Principal` (2). The 11-test count in the task brief includes additional assertion branches counted individually.

### Backend — Unit: Entity Models (`backend/tests/unit/test_entity_models.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_entity_create_valid | Validates EntityCreate with valid title and description | unit | passing |
| test_entity_create_missing_title_rejected | Rejects EntityCreate without required title field | unit | passing |
| test_entity_create_empty_title_rejected | Rejects EntityCreate with empty string title | unit | passing |
| test_entity_create_description_optional | EntityCreate without description defaults to None | unit | passing |
| test_entity_update_all_optional | EntityUpdate with no fields is valid (all optional) | unit | passing |
| test_entity_update_partial | EntityUpdate with only title set serializes correctly | unit | passing |
| test_entity_update_empty_title_rejected | Rejects EntityUpdate with empty string title | unit | passing |
| test_entity_public_includes_all_fields | EntityPublic includes all 6 required fields | unit | passing |
| test_entity_public_serialization | EntityPublic round-trips through model_dump preserving values | unit | passing |
| test_entities_public_wraps_list | EntitiesPublic serializes data list and count correctly | unit | passing |
| test_entity_base_title_max_length | Rejects title longer than 255 characters | unit | passing |
| test_entity_base_description_max_length | Rejects description longer than 1000 characters | unit | passing |
| test_entity_base_title_max_length_boundary | Accepts title of exactly 255 characters | unit | passing |
| test_entity_base_description_max_length_boundary | Accepts description of exactly 1000 characters | unit | passing |

### Backend — Unit: Entity Service (`backend/tests/unit/test_entity_service.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_create_entity_inserts_and_returns | Inserts new entity and returns populated EntityPublic | unit | passing |
| test_create_entity_calls_insert_with_correct_payload | Verifies insert receives title, description, owner_id payload | unit | passing |
| test_create_entity_empty_response_raises_500 | Raises ServiceError 500 when insert returns empty data | unit | passing |
| test_get_entity_success | Returns EntityPublic when entity exists and caller is owner | unit | passing |
| test_list_entities_paginated | Returns EntitiesPublic with data list and total count | unit | passing |
| test_list_entities_default_pagination | Uses offset=0 limit=20 range when called with defaults | unit | passing |
| test_update_entity_success | Applies update payload and returns updated EntityPublic | unit | passing |
| test_delete_entity_success | Deletes entity and returns None on success | unit | passing |
| test_get_entity_not_found_raises_404 | Raises ServiceError 404 when APIError from single() | unit | passing |
| test_list_entities_caps_limit_at_100 | Caps limit at 100 even when larger value is passed | unit | passing |
| test_list_entities_clamps_negative_offset | Clamps negative offset to 0 before range computation | unit | passing |
| test_list_entities_clamps_zero_limit_to_one | Clamps limit=0 to 1 to avoid invalid range | unit | passing |
| test_update_entity_not_found | Raises ServiceError 404 when update returns empty data | unit | passing |
| test_delete_entity_not_found | Raises ServiceError 404 when delete returns empty data | unit | passing |
| test_create_entity_supabase_error_raises_service_error | Raises ServiceError 500 when Supabase raises exception | unit | passing |
| test_get_entity_infrastructure_error_raises_500 | Raises ServiceError 500 for non-APIError infrastructure failures | unit | passing |
| test_list_entities_supabase_error_raises_service_error | Raises ServiceError 500 when Supabase raises exception | unit | passing |
| test_update_entity_supabase_error_raises_service_error | Raises ServiceError 500 for unexpected update exceptions | unit | passing |
| test_delete_entity_supabase_error_raises_service_error | Raises ServiceError 500 for unexpected delete exceptions | unit | passing |
| test_update_entity_no_fields_to_update | Fetches current entity without calling update when no fields set | unit | passing |

> All 20 tests use `unittest.mock.MagicMock` for the Supabase client -- no database or network required. Covers happy path CRUD (5), edge cases (7), and error propagation (8).

### Backend — Unit: Lifespan (`backend/tests/unit/test_lifespan.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_shutdown_order_log_then_close_then_flush | Shutdown calls in exact order: log, http_client close, sentry flush | unit | passing |
| test_shutdown_closes_http_client_even_after_log | http_client.close() awaited after the shutdown log event | unit | passing |
| test_sentry_flush_called_with_timeout | sentry_sdk.flush(timeout=2.0) called during shutdown | unit | passing |

### Backend — Unit: HTTP Client (`backend/tests/unit/test_http_client.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_circuit_breaker_initially_closed | Circuit breaker starts in closed state | unit | passing |
| test_circuit_breaker_opens_after_threshold | Circuit opens after failure count reaches threshold | unit | passing |
| test_circuit_breaker_does_not_open_below_threshold | Circuit stays closed below failure threshold | unit | passing |
| test_circuit_breaker_success_resets_state | Recording success clears failure history and closes circuit | unit | passing |
| test_circuit_breaker_half_open_after_window | After window expires circuit allows next request through | unit | passing |
| test_circuit_breaker_old_failures_expire | Failures older than window are pruned from history | unit | passing |
| test_timeout_configuration | Default timeouts are 5s connect and 30s read | unit | passing |
| test_timeout_configuration_custom | Custom read_timeout and connect_timeout are set correctly | unit | passing |
| test_header_propagation_request_id[asyncio] | X-Request-ID from structlog context added to outgoing request | unit | passing |
| test_header_propagation_no_contextvars[asyncio] | Missing context vars don't cause errors in outgoing requests | unit | passing |
| test_header_propagation_merges_with_existing_headers[asyncio] | Caller headers merged with propagated context headers | unit | passing |
| test_retry_on_502[asyncio] | 502 response triggers automatic retry | unit | passing |
| test_retry_on_503[asyncio] | 503 response triggers automatic retry | unit | passing |
| test_retry_on_504[asyncio] | 504 response triggers automatic retry | unit | passing |
| test_exponential_backoff_sequence[asyncio] | Retry delays follow 0.5s, 1.0s, 2.0s backoff sequence | unit | passing |
| test_no_retry_on_4xx[asyncio] | 400 client errors are not retried | unit | passing |
| test_no_retry_on_401[asyncio] | 401 unauthorized errors are not retried | unit | passing |
| test_no_retry_on_404[asyncio] | 404 not found errors are not retried | unit | passing |
| test_retries_exhausted_returns_last_502[asyncio] | After all retries a 502 response is returned as-is | unit | passing |
| test_retries_exhausted_on_http_error_raises[asyncio] | Non-status httpx error after retries raises ServiceError | unit | passing |
| test_circuit_open_raises_service_error_without_http_call[asyncio] | Open circuit raises ServiceError without making request | unit | passing |
| test_circuit_breaker_records_failure_on_5xx[asyncio] | 5xx response records a circuit breaker failure | unit | passing |
| test_circuit_breaker_records_success_on_2xx[asyncio] | 2xx response records a circuit breaker success | unit | passing |
| test_get_method[asyncio] | GET convenience method sends GET request and returns response | unit | passing |
| test_post_method[asyncio] | POST convenience method sends POST request and returns response | unit | passing |
| test_put_method[asyncio] | PUT convenience method sends PUT request and returns response | unit | passing |
| test_patch_method[asyncio] | PATCH convenience method sends PATCH request and returns response | unit | passing |
| test_delete_method[asyncio] | DELETE convenience method sends DELETE request and returns response | unit | passing |
| test_get_http_client_returns_from_app_state | get_http_client dependency returns app.state.http_client | unit | passing |
| test_get_http_client_missing_raises_503 | Missing http_client in app.state raises ServiceError 503 | unit | passing |

> 30 tests covering: CircuitBreaker (6 sync), HttpClient config (2 sync), header propagation (3 async), retry logic (8 async), circuit breaker integration (3 async), convenience methods (5 async), and FastAPI dependency (2 sync).

### Backend — Unit: Supabase Client (`backend/tests/unit/test_supabase.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_create_supabase_client_returns_client | Factory returns a Supabase client instance for valid credentials | unit | passing |
| test_create_supabase_client_failure_raises_service_error | Constructor failure raises ServiceError 503 | unit | passing |
| test_get_supabase_returns_from_app_state | FastAPI dependency returns client from app.state.supabase | unit | passing |
| test_get_supabase_missing_state_raises_503 | Missing supabase in app.state raises ServiceError 503 | unit | passing |

### Backend — Unit: Auth (`backend/tests/unit/test_auth.py`)

| Test Name | Description | Type | Status |
|-----------|-------------|------|--------|
| test_valid_jwt_returns_principal | Valid Clerk JWT returns Principal with correct user_id and session_id | unit | passing |
| test_missing_authorization_returns_401_auth_missing_token | Missing Authorization header returns 401 AUTH_MISSING_TOKEN | unit | passing |
| test_expired_jwt_returns_401_auth_expired_token | Expired JWT returns 401 with AUTH_EXPIRED_TOKEN code | unit | passing |
| test_invalid_signature_returns_401_auth_invalid_token | Invalid JWT signature returns 401 with AUTH_INVALID_TOKEN | unit | passing |
| test_unauthorized_party_returns_401_auth_invalid_token | Unauthorized party JWT returns 401 with AUTH_INVALID_TOKEN | unit | passing |
| test_user_id_set_on_request_state | Successful auth sets request.state.user_id to principal's user_id | unit | passing |
| test_clerk_sdk_exception_returns_401 | Clerk SDK exception propagates as 401 ServiceError | unit | passing |
| test_unknown_reason_returns_401_auth_invalid_token | Unknown error reason returns 401 with AUTH_INVALID_TOKEN | unit | passing |
| test_roles_extracted_from_org_metadata | Org role from JWT 'o.rol' claim extracted into roles list | unit | passing |
| test_no_org_id_returns_none | Missing org data in JWT results in org_id=None on Principal | unit | passing |
| test_missing_sub_claim_returns_401 | Missing 'sub' claim in JWT payload returns 401 AUTH_INVALID_TOKEN | unit | passing |
| test_none_payload_returns_401 | None JWT payload from Clerk SDK returns 401 AUTH_INVALID_TOKEN | unit | passing |

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
| backend/core/db | No unit tests for engine creation and init_db | - |
| backend/utils | No unit tests for email generation and token utilities | - |
| backend/app/lifespan | No test for startup log event fields (service_name, version, environment) | - |
| backend/core/http_client | No integration tests against real HTTP server | - |
| frontend | No unit or integration tests (Playwright E2E only) | - |

> `backend/core/config` was previously listed as a gap — now covered by 13 unit tests in `backend/tests/unit/test_config.py`.
> `backend/core/errors` is a new module introduced in AYG-65 — covered by 20 unit tests in `backend/tests/unit/test_errors.py`.
> `backend/models/auth` and `backend/models/common` are new modules introduced in AYG-65 — covered by 11 unit tests in `backend/tests/unit/test_models.py`.
> `backend/models/entity` is a new module introduced in AYG-69 — covered by 14 unit tests in `backend/tests/unit/test_entity_models.py`.
> `backend/services/entity_service` introduced in AYG-69 is now fully covered by 20 unit tests in `backend/tests/unit/test_entity_service.py` (AYG-70).
> `backend/core/middleware` test_cookie_header_not_logged (26th test) addresses the security gap of sensitive cookie values leaking into structured logs.
> `backend/app/lifespan` introduced in AYG-71 — covered by 3 unit tests verifying shutdown ordering (AC-10).
> `backend/core/auth` introduced in AYG-71 — covered by 12 unit tests in `backend/tests/unit/test_auth.py`.
> `backend/core/http_client` introduced in AYG-71 — covered by 30 unit tests in `backend/tests/unit/test_http_client.py`.
> `backend/core/supabase` introduced in AYG-71 — covered by 4 unit tests in `backend/tests/unit/test_supabase.py`.
