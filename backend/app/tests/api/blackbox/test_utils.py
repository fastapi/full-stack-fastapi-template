"""
Utilities for blackbox testing to simplify common operations.

This module provides functions for testing common API operations and verification
without any knowledge of the database or implementation details.
"""
import json
import uuid
import random
import string
from typing import Dict, Any, List, Tuple, Optional, Union

from .client_utils import BlackboxClient

def create_random_user(client: BlackboxClient) -> Dict[str, Any]:
    """
    Create a random user and return user data with credentials.
    
    Args:
        client: API client instance
        
    Returns:
        Dictionary with user information and credentials
    """
    # Generate random credentials
    email = f"test-{uuid.uuid4()}@example.com"
    password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    full_name = f"Test User {uuid.uuid4().hex[:8]}"
    
    # Create user and login
    user_data = client.create_and_login_user(email, password, full_name)
    return user_data

def create_test_item(client: BlackboxClient, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a test item and return the item data.
    
    Args:
        client: API client instance
        title: Item title (random if not provided)
        description: Item description (random if not provided)
        
    Returns:
        Item data from API response
    """
    if not title:
        title = f"Test Item {uuid.uuid4().hex[:8]}"
        
    if not description:
        description = f"Test description {uuid.uuid4().hex[:16]}"
    
    response = client.create_item(title=title, description=description)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to create item: {response.text}")
        
    return response.json()

def assert_error_response(response, expected_status_code: int) -> None:
    """
    Assert that a response is an error with expected status code.
    
    Args:
        response: HTTP response
        expected_status_code: Expected HTTP status code
    """
    assert response.status_code == expected_status_code, \
        f"Expected status code {expected_status_code}, got {response.status_code}: {response.text}"
        
    error_data = response.json()
    assert "detail" in error_data, \
        f"Error response missing 'detail' field: {error_data}"

def assert_validation_error(response) -> None:
    """
    Assert that a response is a validation error (422).
    
    Args:
        response: HTTP response
    """
    assert_error_response(response, 422)
    error_data = response.json()
    
    assert isinstance(error_data["detail"], list), \
        f"Validation error should have list of details: {error_data}"
        
    for detail in error_data["detail"]:
        assert "loc" in detail, f"Validation error detail missing 'loc': {detail}"
        assert "msg" in detail, f"Validation error detail missing 'msg': {detail}"
        assert "type" in detail, f"Validation error detail missing 'type': {detail}"

def assert_not_found_error(response) -> None:
    """
    Assert that a response is a not found error (404).
    
    Args:
        response: HTTP response
    """
    assert_error_response(response, 404)

def assert_unauthorized_error(response) -> None:
    """
    Assert that a response is an unauthorized error (401 or 403).
    
    Args:
        response: HTTP response
    """
    assert response.status_code in (401, 403), \
        f"Expected status code 401 or 403, got {response.status_code}: {response.text}"
        
    error_data = response.json()
    assert "detail" in error_data, \
        f"Error response missing 'detail' field: {error_data}"

def create_superuser_client() -> BlackboxClient:
    """
    Create a client authenticated as superuser.
    
    This requires that the server has a superuser account available with
    known credentials from the environment.
    
    Returns:
        Authenticated client instance
    """
    # The superuser credentials should be available in the environment
    # Typically, the first superuser from FIRST_SUPERUSER/FIRST_SUPERUSER_PASSWORD
    import os
    
    superuser_email = os.environ.get("FIRST_SUPERUSER", "admin@example.com")
    superuser_password = os.environ.get("FIRST_SUPERUSER_PASSWORD", "admin")
    
    client = BlackboxClient()
    login_response = client.login(superuser_email, superuser_password)
    
    if login_response.status_code != 200:
        raise ValueError(f"Failed to log in as superuser: {login_response.text}")
        
    return client

def verify_user_object(user_data: Dict[str, Any]) -> None:
    """
    Verify that a user object has the expected structure.
    
    Args:
        user_data: User data from API response
    """
    assert "id" in user_data, "User object missing 'id'"
    assert "email" in user_data, "User object missing 'email'"
    assert "is_active" in user_data, "User object missing 'is_active'"
    assert "is_superuser" in user_data, "User object missing 'is_superuser'"
    assert "full_name" in user_data, "User object missing 'full_name'"
    
    # Password should NEVER be included in user objects
    assert "password" not in user_data, "User object should not include 'password'"
    assert "hashed_password" not in user_data, "User object should not include 'hashed_password'"

def verify_item_object(item_data: Dict[str, Any]) -> None:
    """
    Verify that an item object has the expected structure.
    
    Args:
        item_data: Item data from API response
    """
    assert "id" in item_data, "Item object missing 'id'"
    assert "title" in item_data, "Item object missing 'title'"
    assert "owner_id" in item_data, "Item object missing 'owner_id'"
    # Note: description is optional in the schema

def assert_uuid_format(value: str) -> bool:
    """Check if a string is a valid UUID format."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False