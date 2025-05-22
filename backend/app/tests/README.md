# KonditionFastAPI Backend Testing Framework

This directory contains the testing framework for the KonditionFastAPI backend. The framework is built using pytest and follows test-driven development principles.

## Test Structure

The tests are organized as follows:

```
tests/
├── __init__.py
├── conftest.py                # Pytest fixtures and configuration
├── api/                       # API endpoint tests
│   ├── __init__.py
│   ├── routes/                # Tests for API routes
│   │   ├── __init__.py
│   │   ├── test_auth.py       # Authentication tests
│   │   ├── test_items.py      # Item API tests
│   │   ├── test_login.py      # Login API tests
│   │   ├── test_private.py    # Private API tests
│   │   ├── test_social.py     # Social features tests
│   │   └── test_users.py      # User API tests
├── crud/                      # CRUD operation tests
│   ├── __init__.py
│   └── test_user.py           # User CRUD tests
└── utils/                     # Test utilities
    ├── __init__.py
    ├── test_client.py         # Test client utilities
    ├── test_db.py             # Database testing utilities
    ├── user.py                # User testing utilities
    └── utils.py               # General testing utilities
```

## Test Database

The tests use an in-memory SQLite database for fast execution. The database is created fresh for each test function, ensuring test isolation.

## Test Client

The test client is a wrapper around FastAPI's TestClient that provides helper methods for making API requests and handling authentication.

## Running Tests

To run the tests, use the following command from the backend directory:

```bash
# Run all tests
bash scripts/test.sh

# Run specific tests
pytest app/tests/api/routes/test_auth.py -v

# Run tests with coverage report
coverage run --source=app -m pytest
coverage report --show-missing
coverage html
```

## Writing Tests

When writing tests, follow these guidelines:

1. **Test Isolation**: Each test should be independent and not rely on the state from other tests.
2. **Use Fixtures**: Use pytest fixtures for setup and teardown.
3. **Mock External Services**: Use monkeypatch to mock external services like email sending.
4. **Test Both Success and Failure Cases**: Test both valid and invalid inputs.
5. **Use Helper Functions**: Use the provided helper functions for common operations.

## Test Utilities

The framework provides several utilities to make testing easier:

- `test_client.py`: Provides a wrapper around FastAPI's TestClient with helper methods.
- `test_db.py`: Provides utilities for database operations during tests.
- `user.py`: Provides utilities for creating and authenticating users.
- `utils.py`: Provides general utilities like generating random strings and emails.

## Authentication in Tests

To test authenticated endpoints, use the provided fixtures:

```python
def test_authenticated_endpoint(test_client, normal_user_token_headers):
    response = test_client.get("/protected-endpoint", headers=normal_user_token_headers)
    assert response.status_code == 200
```

Or use the TestClientWrapper to login:

```python
def test_authenticated_endpoint(test_client, db):
    # Create a user
    user = create_test_user(db)
    
    # Login
    auth_headers = test_client.login(user.email, "testpassword")
    
    # Make authenticated request
    response = test_client.get("/protected-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Continuous Integration

The tests are run automatically in the CI pipeline. Make sure all tests pass before submitting a pull request.