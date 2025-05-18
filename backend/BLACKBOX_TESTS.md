# Blackbox Testing Strategy for Modular Monolith Refactoring

This document outlines a comprehensive blackbox testing approach to ensure that the behavior of the FastAPI backend remains consistent before and after the modular monolith refactoring.

## Current Implementation Status

**✅ New implementation complete!** We have now set up the following:

- A fully external HTTP-based testing approach using httpx
- Tests run against a real running server without TestClient
- No direct database manipulation in tests
- Helper utilities for interacting with the API
- Proper server lifecycle management during tests
- Clean separation of API testing from implementation details

This is a significant improvement over the previous implementation, which used:
- TestClient (FastAPI's built-in testing client)
- Direct access to the database
- Knowledge of internal implementation details

## Test Principles

1. **True Blackbox Testing**: Tests interact with the API solely through HTTP requests, just like any external client would
2. **No Implementation Knowledge**: Tests have no knowledge of internal implementation details
3. **Stateless Tests**: Tests do not rely on database state between tests
4. **Independent Execution**: Tests can run against any server instance (local, Docker, remote)
5. **Before/After Validation**: Tests can be run before and after each refactoring phase

## Test Implementation

### Test Infrastructure

The blackbox tests use the following components:

1. **httpx**: A modern HTTP client for Python
2. **pytest**: The testing framework for organizing and running tests
3. **BlackboxClient**: A custom client that wraps httpx with API-specific helpers
4. **Test utilities**: Helper functions for common operations and assertions

### Running Tests

Tests can be run using the included run_blackbox_tests.sh script:

```bash
cd backend
bash scripts/run_blackbox_tests.sh
```

The script:
1. Starts a FastAPI server if one is not already running
2. Runs the tests against the running server
3. Generates test reports
4. Stops the server if it was started by the script

### Client Utilities

The BlackboxClient provides an interface for interacting with the API:

```python
# Create a client
client = BlackboxClient()

# Create a user
signup_response, user_data = client.sign_up(
    email="test@example.com",
    password="testpassword123",
    full_name="Test User"
)

# Login to get a token
login_response = client.login("test@example.com", "testpassword123")

# The token is automatically stored and used in subsequent requests
user_profile = client.get("/api/v1/users/me")

# Create an item
item_response = client.create_item("Test Item", "Test Description")
item_id = item_response.json()["id"]

# Update an item
update_response = client.put(f"/api/v1/items/{item_id}", json_data={
    "title": "Updated Item"
})

# Delete an item
client.delete(f"/api/v1/items/{item_id}")
```

## Test Categories

### API Contract Tests

Verify that API endpoints adhere to their expected contracts:
- Response schemas
- Status codes
- Validation rules

```python
def test_user_signup_contract(client):
    # Test user signup returns the expected response structure
    response, _ = client.sign_up(
        email=f"test-{uuid.uuid4()}@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    
    result = response.json()
    verify_user_object(result)  # Check schema fields exist
    
    # Verify validation errors
    invalid_response, _ = client.sign_up(email="not-an-email", password="testpassword123")
    assert_validation_error(invalid_response)
```

### User Lifecycle Tests

Verify complete end-to-end user flows:

```python
def test_complete_user_lifecycle(client):
    # Create a user
    signup_response, credentials = client.sign_up()
    
    # Login
    client.login(credentials["email"], credentials["password"])
    
    # Create an item
    item_response = client.create_item("Test Item")
    item_id = item_response.json()["id"]
    
    # Update the item
    client.put(f"/api/v1/items/{item_id}", json_data={"title": "Updated Item"})
    
    # Delete the item
    client.delete(f"/api/v1/items/{item_id}")
    
    # Delete the user
    client.delete("/api/v1/users/me")
    
    # Verify user is deleted by trying to login again
    new_client = BlackboxClient()
    login_response = new_client.login(credentials["email"], credentials["password"])
    assert login_response.status_code != 200
```

### Authorization Tests

Verify that authorization rules are enforced:

```python
def test_resource_ownership_protection(client):
    # Create two users
    user1_client = BlackboxClient()
    user1_client.create_and_login_user()
    
    user2_client = BlackboxClient()
    user2_client.create_and_login_user()
    
    # User1 creates an item
    item_response = user1_client.create_item("User1 Item")
    item_id = item_response.json()["id"]
    
    # User2 attempts to access User1's item
    user2_get_response = user2_client.get(f"/api/v1/items/{item_id}")
    assert user2_get_response.status_code == 404, "User2 should not see User1's item"
```

## Test Execution Plan

### Pre-Refactoring Phase

1. Run the complete test suite against the current architecture
2. Establish a baseline of expected responses and behaviors
3. Create a test report documenting the current behavior

### During Refactoring Phase

1. After each module refactoring, run the relevant subset of tests
2. Verify that the refactored module maintains the same external behavior
3. Document any differences or issues encountered

### Post-Refactoring Phase

1. Run the complete test suite against the fully refactored architecture
2. Compare results with the pre-refactoring baseline
3. Verify all tests pass with the same results as before refactoring
4. Create a final test report documenting the comparison

## Dependencies and Setup

The tests require the following:

1. httpx: `pip install httpx`
2. pytest: `pip install pytest`
3. A running FastAPI server (started automatically by the test script if not running)
4. The superuser credentials in environment variables (for admin tests)

## Continuous Integration Integration

Add the blackbox tests to the CI/CD pipeline to ensure they run on every pull request:

```yaml
# .github/workflows/backend-tests.yml (example)
name: Backend Tests

jobs:
  blackbox-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: app_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        cd backend
        pip install -e .
        pip install pytest pytest-html httpx
        
    - name: Run blackbox tests
      run: |
        cd backend
        bash scripts/run_blackbox_tests.sh
        
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-reports
        path: backend/test-reports/
```

## Conclusion

This blackbox testing strategy ensures that the external behavior of the API remains consistent throughout the refactoring process. By focusing exclusively on HTTP interactions without any knowledge of implementation details, these tests provide the most reliable validation that the refactoring does not introduce changes in behavior from an external client's perspective.