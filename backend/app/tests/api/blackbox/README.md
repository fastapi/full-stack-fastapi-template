# Blackbox Tests

This directory contains blackbox tests for the API. These tests interact with a running API server via HTTP requests, without any knowledge of the internal implementation.

## Test Approach

- Tests use httpx to make real HTTP requests to a running server
- No direct database manipulation - all data is created/read/updated/deleted via the API
- Tests have no knowledge of internal implementation details
- Tests can be run against any server (local, Docker, remote)

## Running the Tests

Tests can be run using the included script:

```bash
cd backend
bash scripts/run_blackbox_tests.sh
```

The script will:
1. Check if a server is already running, or start one if needed
2. Run the basic infrastructure tests first
3. If they pass, run the full test suite
4. Generate test reports
5. Stop the server if it was started by the script

## Test Categories

- **Basic Tests**: Verify server is running and basic API functionality works
- **API Contract Tests**: Verify API endpoints adhere to their contracts
- **User Lifecycle Tests**: Verify complete user flows from creation to deletion
- **Authorization Tests**: Verify permission rules are enforced correctly

## Client Utilities

The `client_utils.py` module provides a `BlackboxClient` class that wraps httpx with API-specific helpers. This simplifies test writing and maintenance.

Example usage:

```python
# Create a client
client = BlackboxClient()

# Create a user
signup_response, credentials = client.sign_up(
    email="test@example.com",
    password="testpassword123",
    full_name="Test User"
)

# Login to get a token
client.login(credentials["email"], credentials["password"])

# The token is automatically stored and used in subsequent requests
user_profile = client.get("/api/v1/users/me")

# Create an item
item = client.create_item("Test Item", "Description").json()
```

## Test Utilities

The `test_utils.py` module provides helper functions for common test operations and assertions:

- `create_random_user`: Create a user with random data
- `create_test_item`: Create a test item for a user
- `assert_validation_error`: Verify a 422 validation error response
- `assert_not_found_error`: Verify a 404 not found error response
- `assert_unauthorized_error`: Verify a 401/403 unauthorized error response
- `verify_user_object`: Verify a user object has the expected structure
- `verify_item_object`: Verify an item object has the expected structure

## Environment Variables

The tests use the following environment variables:

- `TEST_SERVER_URL`: URL of the API server (default: http://localhost:8000)
- `TEST_REQUEST_TIMEOUT`: Request timeout in seconds (default: 30.0)
- `FIRST_SUPERUSER`: Email of the superuser account for admin tests
- `FIRST_SUPERUSER_PASSWORD`: Password of the superuser account

## Admin Tests

Some tests require a superuser account to run. These tests will be skipped if:

1. No superuser credentials are provided in environment variables
2. The superuser login fails

If you want to run admin tests, ensure the superuser exists in the database and provide valid credentials in the environment variables.