"""
Blackbox test for API contracts.

This test verifies that API endpoints adhere to their expected contracts:
- Response schemas conform to specifications
- Status codes are correct for different scenarios
- Validation rules are properly enforced
"""
import uuid
from typing import Dict, Any

import pytest
import httpx

from .client_utils import BlackboxClient
from .test_utils import (
    assert_validation_error,
    assert_not_found_error,
    assert_unauthorized_error,
    assert_uuid_format,
    verify_user_object,
    verify_item_object
)

def test_user_signup_contract(client):
    """Test that user signup endpoint adheres to contract."""
    user_data = {
        "email": f"signup-{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "full_name": "Signup Test User"
    }
    
    # Test the signup endpoint
    response, _ = client.sign_up(
        email=user_data["email"],
        password=user_data["password"],
        full_name=user_data["full_name"]
    )
    
    assert response.status_code == 200, f"Signup failed: {response.text}"
    
    result = response.json()
    # Verify response schema by checking all required fields
    verify_user_object(result)
    
    # Verify field values
    assert result["email"] == user_data["email"]
    assert result["full_name"] == user_data["full_name"]
    assert result["is_active"] is True
    assert result["is_superuser"] is False
    
    # Verify UUID format
    assert assert_uuid_format(result["id"]), "User ID is not a valid UUID"
    
    # Test validation errors
    # 1. Test invalid email format
    invalid_email_response, _ = client.sign_up(
        email="not-an-email",
        password="testpassword123",
        full_name="Validation Test"
    )
    assert_validation_error(invalid_email_response)
    
    # 2. Test short password
    short_pw_response, _ = client.sign_up(
        email="test@example.com",
        password="short",
        full_name="Validation Test"
    )
    assert_validation_error(short_pw_response)

def test_login_contract(client):
    """Test that login endpoint adheres to contract."""
    # Create a user first
    unique_email = f"login-{uuid.uuid4()}@example.com"
    password = "testpassword123"
    
    signup_response, _ = client.sign_up(
        email=unique_email,
        password=password,
        full_name="Login Test User"
    )
    assert signup_response.status_code == 200
    
    # Test login with the credentials
    login_response = client.login(unique_email, password)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    result = login_response.json()
    # Verify response schema
    assert "access_token" in result
    assert "token_type" in result
    
    # Verify token type
    assert result["token_type"].lower() == "bearer"
    
    # Verify token format (non-empty string)
    assert isinstance(result["access_token"], str)
    assert len(result["access_token"]) > 0
    
    # Test login with wrong credentials
    wrong_login_response = client.post("/api/v1/login/access-token", data={
        "username": unique_email,
        "password": "wrongpassword"
    })
    assert wrong_login_response.status_code in (400, 401), \
        f"Expected 400/401 for wrong password, got: {wrong_login_response.status_code}"
        
    # Test login with non-existent user
    nonexistent_login_response = client.post("/api/v1/login/access-token", data={
        "username": f"nonexistent-{uuid.uuid4()}@example.com",
        "password": "testpassword123"
    })
    assert nonexistent_login_response.status_code in (400, 401), \
        f"Expected 400/401 for nonexistent user, got: {nonexistent_login_response.status_code}"

def test_me_endpoint_contract(client):
    """Test that /users/me endpoint adheres to contract."""
    # Create a user and log in
    user_data = client.create_and_login_user()
    
    # Test /users/me endpoint
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200, f"Get user profile failed: {response.text}"
    
    result = response.json()
    # Verify response schema
    verify_user_object(result)
    
    # Verify field values
    assert result["email"] == user_data["credentials"]["email"]
    assert result["full_name"] == user_data["credentials"]["full_name"]
    
    # Test unauthorized access
    # Create a new client without authentication
    unauthenticated_client = BlackboxClient(base_url=client.base_url)
    unauthenticated_response = unauthenticated_client.get("/api/v1/users/me")
    assert_unauthorized_error(unauthenticated_response)

def test_create_item_contract(client):
    """Test that item creation endpoint adheres to contract."""
    # Create a user and log in
    client.create_and_login_user()
    
    # Create an item
    item_data = {
        "title": "Test Item",
        "description": "Test Description"
    }
    
    response = client.create_item(
        title=item_data["title"],
        description=item_data["description"]
    )
    
    assert response.status_code == 200, f"Create item failed: {response.text}"
    
    result = response.json()
    # Verify response schema
    assert "id" in result
    assert "title" in result
    assert "description" in result
    assert "owner_id" in result
    
    # Verify field values
    assert result["title"] == item_data["title"]
    assert result["description"] == item_data["description"]
    
    # Verify UUID format
    assert assert_uuid_format(result["id"])
    assert assert_uuid_format(result["owner_id"])
    
    # Test validation errors
    # Missing required field (title)
    invalid_response = client.post("/api/v1/items/", json_data={
        "description": "Missing Title"
    })
    assert_validation_error(invalid_response)

def test_get_items_contract(client):
    """Test that items list endpoint adheres to contract."""
    # Create a user and log in
    client.create_and_login_user()
    
    # Create a few items
    created_items = []
    for i in range(3):
        item_response = client.create_item(
            title=f"Item {i}",
            description=f"Description {i}"
        )
        if item_response.status_code == 200:
            created_items.append(item_response.json())
    
    # Get items list
    response = client.get("/api/v1/items/")
    assert response.status_code == 200, f"Get items failed: {response.text}"
    
    result = response.json()
    # Verify response schema
    assert "data" in result
    assert "count" in result
    assert isinstance(result["data"], list)
    assert isinstance(result["count"], int)
    
    # Verify items schema
    if len(result["data"]) > 0:
        for item in result["data"]:
            verify_item_object(item)
    
    # Verify count matches actual items returned
    assert result["count"] == len(result["data"])
    
    # Verify pagination
    if len(result["data"]) > 1:
        # Test with limit parameter
        limit = 1
        limit_response = client.get(f"/api/v1/items/?limit={limit}")
        assert limit_response.status_code == 200
        limit_result = limit_response.json()
        assert len(limit_result["data"]) <= limit
        
        # Test with skip parameter
        skip = 1
        skip_response = client.get(f"/api/v1/items/?skip={skip}")
        assert skip_response.status_code == 200

def test_not_found_contract(client):
    """Test that not found errors follow the expected format."""
    # Create a user and log in
    client.create_and_login_user()
    
    # Test with non-existent item
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/items/{non_existent_id}")
    assert_not_found_error(response)
    
    # Test with non-existent user (admin endpoint)
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/users/{non_existent_id}")
    assert response.status_code in (403, 404), \
        f"Expected 403/404 for non-admin or non-existent, got: {response.status_code}"

def test_validation_error_contract(client):
    """Test that validation errors follow the expected format."""
    # Create invalid user data
    invalid_data = {
        "email": "not-an-email",
        "password": "testpassword123",
        "full_name": "Validation Test"
    }
    response = client.post("/api/v1/users/signup", json_data=invalid_data)
    assert_validation_error(response)
    
    # Test with short password
    short_pw_data = {
        "email": "test@example.com",
        "password": "short",
        "full_name": "Validation Test"
    }
    response = client.post("/api/v1/users/signup", json_data=short_pw_data)
    assert_validation_error(response)
    
    # Test with missing required field
    missing_data = {"email": "test@example.com"}
    response = client.post("/api/v1/users/signup", json_data=missing_data)
    assert_validation_error(response)

def test_update_item_contract(client):
    """Test that item update endpoint adheres to contract."""
    # Create a user and log in
    client.create_and_login_user()
    
    # Create an item first
    item_data = {
        "title": "Original Item",
        "description": "Original Description"
    }
    create_response = client.create_item(
        title=item_data["title"],
        description=item_data["description"]
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Update the item
    update_data = {
        "title": "Updated Item",
        "description": "Updated Description"
    }
    update_response = client.put(f"/api/v1/items/{item_id}", json_data=update_data)
    assert update_response.status_code == 200, f"Update item failed: {update_response.text}"
    
    result = update_response.json()
    # Verify response schema
    assert "id" in result
    assert "title" in result
    assert "description" in result
    assert "owner_id" in result
    
    # Verify field values are updated
    assert result["title"] == update_data["title"]
    assert result["description"] == update_data["description"]
    
    # ID and owner should remain the same
    assert result["id"] == item_id
    
    # Test validation errors on update
    invalid_update_data = {"title": ""}  # Empty title should be invalid
    invalid_response = client.put(f"/api/v1/items/{item_id}", json_data=invalid_update_data)
    assert_validation_error(invalid_response)

def test_unauthorized_contract(client):
    """Test that unauthorized errors follow the expected format."""
    # Create a regular client without authentication
    unauthenticated_client = BlackboxClient(base_url=client.base_url)
    
    # Test protected endpoint with invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = unauthenticated_client.get("/api/v1/users/me", headers=headers)
    assert_unauthorized_error(response)
    
    # Test protected endpoint with no token
    response = unauthenticated_client.get("/api/v1/users/me")
    assert_unauthorized_error(response)
    
    # Test protected endpoint with expired token
    # This is hard to test in a blackbox manner without manipulating tokens
    # For now, we'll just assert that the server handles auth errors consistently
    
    # Create a user and authenticate
    client.create_and_login_user()
    
    # Try to access resources that require different permissions
    # Regular user attempt to access admin endpoints
    users_response = client.get("/api/v1/users/")
    assert users_response.status_code in (401, 403, 404), \
        f"Expected permission error, got: {users_response.status_code}"