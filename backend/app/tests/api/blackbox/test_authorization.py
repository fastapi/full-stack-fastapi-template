"""
Blackbox test for authorization rules.

This test verifies that authorization is properly enforced 
across different user roles and resource access scenarios,
using only HTTP requests to a running server.
"""
import os
import uuid
import pytest
from typing import Dict, Any

from .client_utils import BlackboxClient
from .test_utils import assert_unauthorized_error

def test_role_based_access(client, admin_client):
    """Test that different user roles have appropriate access restrictions."""
    # Skip if admin client wasn't created successfully
    if not admin_client.token:
        pytest.skip("Admin client not available (login failed)")
        
    # Create a regular user
    regular_client = BlackboxClient(base_url=client.base_url)
    regular_user_data = regular_client.create_and_login_user()
    
    # 1. Test admin-only endpoint access - list all users
    regular_list_response = regular_client.get("/api/v1/users/")
    assert regular_list_response.status_code in (401, 403, 404), \
        f"Regular user shouldn't access admin endpoint, got: {regular_list_response.status_code}"
    
    admin_list_response = admin_client.get("/api/v1/users/")
    assert admin_list_response.status_code == 200, \
        f"Admin should access admin endpoints: {admin_list_response.text}"
    
    # 2. Test admin-only endpoint - create new user
    new_user_data = {
        "email": f"newuser-{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "full_name": "New Test User",
        "is_superuser": False
    }
    
    regular_create_response = regular_client.post("/api/v1/users/", json_data=new_user_data)
    assert regular_create_response.status_code in (401, 403, 404), \
        f"Regular user shouldn't create users via admin endpoint, got: {regular_create_response.status_code}"
    
    admin_create_response = admin_client.post("/api/v1/users/", json_data=new_user_data)
    assert admin_create_response.status_code == 200, \
        f"Admin should create users: {admin_create_response.text}"
    
    # Get the created user ID for later tests
    created_user_id = admin_create_response.json()["id"]
    
    # 3. Test admin-only endpoint - get specific user
    regular_get_response = regular_client.get(f"/api/v1/users/{created_user_id}")
    assert regular_get_response.status_code in (401, 403, 404), \
        f"Regular user shouldn't access other user details, got: {regular_get_response.status_code}"
    
    admin_get_response = admin_client.get(f"/api/v1/users/{created_user_id}")
    assert admin_get_response.status_code == 200, \
        f"Admin should access user details: {admin_get_response.text}"
    
    # 4. Test shared endpoint with different permissions - sending test email
    regular_email_response = regular_client.post(
        "/api/v1/utils/test-email/", 
        json_data={"email_to": regular_user_data["credentials"]["email"]}
    )
    assert regular_email_response.status_code in (401, 403, 404), \
        f"Regular user shouldn't send test emails, got: {regular_email_response.status_code}"
    
    admin_email_response = admin_client.post(
        "/api/v1/utils/test-email/", 
        json_data={"email_to": "admin@example.com"}
    )
    assert admin_email_response.status_code == 200, \
        f"Admin should send test emails: {admin_email_response.text}"

def test_resource_ownership_protection(client):
    """Test that users can only access their own resources."""
    # Create two users with separate clients
    user1_client = BlackboxClient(base_url=client.base_url)
    user1_data = user1_client.create_and_login_user(
        email=f"user1-{uuid.uuid4()}@example.com"
    )
    
    user2_client = BlackboxClient(base_url=client.base_url)
    user2_data = user2_client.create_and_login_user(
        email=f"user2-{uuid.uuid4()}@example.com"
    )
    
    # Create an admin client
    admin_client = BlackboxClient(base_url=client.base_url)
    admin_login = admin_client.login(
        os.environ.get("FIRST_SUPERUSER", "admin@example.com"),
        os.environ.get("FIRST_SUPERUSER_PASSWORD", "admin")
    )
    
    if admin_login.status_code != 200:
        pytest.skip("Admin login failed, skipping admin tests")
    
    # 1. User1 creates an item
    item_data = {"title": "User1 Item", "description": "Test Description"}
    item_response = user1_client.create_item(
        title=item_data["title"],
        description=item_data["description"]
    )
    assert item_response.status_code == 200, f"Create item failed: {item_response.text}"
    item = item_response.json()
    item_id = item["id"]
    
    # 2. User2 attempts to access User1's item
    user2_get_response = user2_client.get(f"/api/v1/items/{item_id}")
    assert user2_get_response.status_code == 404, \
        f"User2 should not see User1's item, got: {user2_get_response.status_code}"
    
    # 3. User2 attempts to update User1's item
    update_data = {"title": "Modified by User2"}
    user2_update_response = user2_client.put(
        f"/api/v1/items/{item_id}", 
        json_data=update_data
    )
    assert user2_update_response.status_code in (403, 404), \
        f"User2 should not update User1's item, got: {user2_update_response.status_code}"
    
    # 4. User2 attempts to delete User1's item
    user2_delete_response = user2_client.delete(f"/api/v1/items/{item_id}")
    assert user2_delete_response.status_code in (403, 404), \
        f"User2 should not delete User1's item, got: {user2_delete_response.status_code}"
    
    # 5. Admin can access User1's item (if admin login successful)
    if admin_client.token:
        admin_get_response = admin_client.get(f"/api/v1/items/{item_id}")
        assert admin_get_response.status_code == 200, \
            f"Admin should access any item: {admin_get_response.text}"
    
    # 6. User1 can access their own item
    user1_get_response = user1_client.get(f"/api/v1/items/{item_id}")
    assert user1_get_response.status_code == 200, \
        f"User1 should access own item: {user1_get_response.text}"
    
    # 7. User1 can update their own item
    user1_update_data = {"title": "Modified by User1"}
    user1_update_response = user1_client.put(
        f"/api/v1/items/{item_id}", 
        json_data=user1_update_data
    )
    assert user1_update_response.status_code == 200, \
        f"User1 should update own item: {user1_update_response.text}"
    assert user1_update_response.json()["title"] == user1_update_data["title"]
    
    # 8. User1 can delete their own item
    user1_delete_response = user1_client.delete(f"/api/v1/items/{item_id}")
    assert user1_delete_response.status_code == 200, \
        f"User1 should delete own item: {user1_delete_response.text}"
    
    # 9. Verify item is deleted
    get_deleted_response = user1_client.get(f"/api/v1/items/{item_id}")
    assert get_deleted_response.status_code == 404, \
        "Deleted item should not be accessible"

def test_unauthenticated_access(client):
    """Test that unauthenticated requests are properly restricted."""
    # Create client without authentication
    unauthenticated_client = BlackboxClient(base_url=client.base_url)
    
    # 1. Protected endpoints should reject unauthenticated requests
    protected_endpoints = [
        "/api/v1/users/me",
        "/api/v1/users/",
        "/api/v1/items/",
    ]
    
    for endpoint in protected_endpoints:
        response = unauthenticated_client.get(endpoint)
        assert response.status_code in (401, 403, 404), \
            f"Unauthenticated request to {endpoint} should be rejected, got: {response.status_code}"
    
    # 2. Public endpoints should allow unauthenticated access
    signup_data = {
        "email": f"public-{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "full_name": "Public Access Test"
    }
    signup_response, _ = unauthenticated_client.sign_up(
        email=signup_data["email"],
        password=signup_data["password"],
        full_name=signup_data["full_name"]
    )
    assert signup_response.status_code == 200, \
        f"Public signup endpoint should be accessible: {signup_response.text}"