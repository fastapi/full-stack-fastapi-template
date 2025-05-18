# Blackbox Testing Strategy

This document outlines a comprehensive blackbox testing approach to ensure that the behavior of the FastAPI backend is thoroughly tested from an external client's perspective.

## Blackbox Testing Principles

1. **True External Testing**: Tests interact with the API solely through HTTP requests, just like any external client would
2. **No Implementation Knowledge**: Tests have no knowledge of internal implementation details
3. **Stateless Tests**: Tests do not rely on database state between tests
4. **Independent Execution**: Tests can run against any server instance (local, Docker, remote)

## Test Infrastructure

The blackbox tests use the following components:

1. **httpx**: A modern HTTP client for Python
2. **pytest**: The testing framework for organizing and running tests
3. **BlackboxClient**: A custom client that wraps httpx with API-specific helpers
4. **Test utilities**: Helper functions for common operations and assertions

## Running Tests

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

## Client Utilities

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

## Test Setup in CI/CD

The blackbox tests are integrated into the CI/CD pipeline to ensure they run on every pull request:

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

## Benefits of Blackbox Testing

1. **Architecture Independence**: Tests remain valid regardless of internal code changes
2. **Refactoring Safety**: Refactoring the codebase doesn't require changing tests as long as the API behavior remains the same
3. **Client Perspective**: Tests verify the application from the client's perspective
4. **Documentation**: Tests serve as executable documentation of the API's behavior
5. **Regression Detection**: Changes that break client compatibility are quickly detected

## Implementation Details

The blackbox testing code is located in:

```
backend/app/tests/api/blackbox/
├── README.md
├── client_utils.py           # Client utilities and helpers
├── conftest.py               # Test fixtures
├── test_api_contract.py      # API contract tests
├── test_authorization.py     # Authorization tests
├── test_basic.py             # Basic functionality tests
├── test_user_lifecycle.py    # User lifecycle tests
└── test_utils.py             # Testing utilities
```