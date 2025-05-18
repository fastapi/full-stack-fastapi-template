"""
Configuration and fixtures for blackbox tests.

These tests are designed to test the API as a black box, without any knowledge
of its implementation details. They interact with a running server via HTTP
and do not directly manipulate the database.
"""
import os
import uuid
import time
import pytest
import httpx
from typing import Dict, Any, Generator, Optional

from .client_utils import BlackboxClient

# Set default timeout for test cases
DEFAULT_TIMEOUT = 30.0  # seconds

# Get server URL from environment or use default
DEFAULT_TEST_SERVER_URL = "http://localhost:8000"
TEST_SERVER_URL = os.environ.get("TEST_SERVER_URL", DEFAULT_TEST_SERVER_URL)

# Superuser credentials for admin tests
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin" 
ADMIN_EMAIL = os.environ.get("FIRST_SUPERUSER", DEFAULT_ADMIN_EMAIL)
ADMIN_PASSWORD = os.environ.get("FIRST_SUPERUSER_PASSWORD", DEFAULT_ADMIN_PASSWORD)

@pytest.fixture(scope="session")
def server_url() -> str:
    """Get the URL of the test server."""
    return TEST_SERVER_URL

@pytest.fixture(scope="session")
def verify_server(server_url: str) -> bool:
    """Verify that the server is running and accessible."""
    # Use the Swagger docs endpoint to check if server is running
    docs_url = f"{server_url}/docs"
    max_retries = 30
    delay = 1.0
    
    print(f"\nChecking if API server is running at {server_url}...")
    
    for attempt in range(max_retries):
        try:
            response = httpx.get(docs_url, timeout=DEFAULT_TIMEOUT)
            if response.status_code == 200:
                print(f"✓ Server is running at {server_url}")
                return True
            
            print(f"Attempt {attempt + 1}/{max_retries}: Server returned {response.status_code}")
        except httpx.RequestError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: {e}")
            
        time.sleep(delay)
        
    # If we reach here, the server is not available
    pytest.fail(f"ERROR: Server not running at {server_url}. "
                f"Run 'docker compose up -d' or 'fastapi dev app/main.py' to start the server.")
    return False  # This line won't be reached due to pytest.fail, but keeps type checking happy

@pytest.fixture(scope="function")
def client(verify_server) -> Generator[BlackboxClient, None, None]:
    """
    Get a BlackboxClient instance connected to the test server.
    
    This fixture verifies that the server is running before creating the client.
    """
    with BlackboxClient(base_url=TEST_SERVER_URL) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def user_client(client) -> Dict[str, Any]:
    """
    Get a client instance authenticated as a regular user.
    
    Returns a dictionary with:
    - client: Authenticated BlackboxClient instance
    - user_data: Dictionary with user information from signup
    - credentials: Dictionary with user credentials
    """
    # Create a random user
    unique_email = f"test-{uuid.uuid4()}@example.com"
    user_password = "testpassword123"
    
    # Sign up and login
    signup_response = client.sign_up(
        email=unique_email,
        password=user_password,
        full_name="Test User"
    )
    
    # Create a new client instance to avoid token sharing
    user_client = BlackboxClient(base_url=TEST_SERVER_URL)
    login_response = user_client.login(unique_email, user_password)
    
    return {
        "client": user_client,
        "user_data": signup_response[0].json(),
        "credentials": signup_response[1]
    }

@pytest.fixture(scope="function")
def admin_client() -> Generator[BlackboxClient, None, None]:
    """
    Get a client instance authenticated as a superuser/admin.
    
    This fixture attempts to log in with the superuser credentials
    from environment variables or defaults.
    """
    with BlackboxClient(base_url=TEST_SERVER_URL) as admin_client:
        login_response = admin_client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        if login_response.status_code != 200:
            pytest.skip("Admin authentication failed. Ensure the superuser exists.")
            
        yield admin_client

@pytest.fixture(scope="function")
def user_and_items(client) -> Dict[str, Any]:
    """
    Create a user with test items and return client and item data.
    
    Returns a dictionary with:
    - client: Authenticated BlackboxClient instance
    - user_data: User information
    - credentials: User credentials
    - items: List of items created for the user
    """
    # Create user
    user_data = client.create_and_login_user()
    
    # Create test items
    items = []
    for i in range(3):
        response = client.create_item(
            title=f"Test Item {i}",
            description=f"Test Description {i}"
        )
        if response.status_code == 200:
            items.append(response.json())
            
    return {
        "client": client,
        "user_data": user_data["signup_response"],
        "credentials": user_data["credentials"],
        "items": items
    }