"""
Blackbox test for complete user lifecycle.

This test verifies that the entire user flow works correctly,
from registration to deletion, including creating, updating and
deleting items, all via HTTP requests to a running server.
"""
import uuid
import pytest
from typing import Dict, Any

from .client_utils import BlackboxClient
from .test_utils import create_random_user, assert_uuid_format

def test_complete_user_lifecycle(client):
    """Test the complete lifecycle of a user including authentication and item management."""
    # 1. Create a user (signup)
    signup_data = {
        "email": f"lifecycle-{uuid.uuid4()}@example.com", 
        "password": "testpassword123", 
        "full_name": "Lifecycle Test"
    }
    signup_response, credentials = client.sign_up(
        email=signup_data["email"],
        password=signup_data["password"],
        full_name=signup_data["full_name"]
    )
    
    assert signup_response.status_code == 200, f"Signup failed: {signup_response.text}"
    user_data = signup_response.json()
    assert_uuid_format(user_data["id"])
    
    # 2. Login with the new user
    login_response = client.login(
        email=signup_data["email"],
        password=signup_data["password"]
    )
    
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    tokens = login_response.json()
    assert "access_token" in tokens
    
    # 3. Get user profile with token
    profile_response = client.get("/api/v1/users/me")
    assert profile_response.status_code == 200, f"Get profile failed: {profile_response.text}"
    user_profile = profile_response.json()
    assert user_profile["email"] == signup_data["email"]
    
    # 4. Update user details
    update_data = {"full_name": "Updated Name"}
    update_response = client.patch("/api/v1/users/me", json_data=update_data)
    assert update_response.status_code == 200, f"Update user failed: {update_response.text}"
    updated_data = update_response.json()
    assert updated_data["full_name"] == update_data["full_name"]
    
    # 5. Create an item
    item_data = {"title": "Test Item", "description": "Test Description"}
    item_response = client.create_item(
        title=item_data["title"], 
        description=item_data["description"]
    )
    
    assert item_response.status_code == 200, f"Create item failed: {item_response.text}"
    item = item_response.json()
    item_id = item["id"]
    assert_uuid_format(item_id)
    
    # 6. Get the item
    get_item_response = client.get(f"/api/v1/items/{item_id}")
    assert get_item_response.status_code == 200, f"Get item failed: {get_item_response.text}"
    assert get_item_response.json()["title"] == item_data["title"]
    
    # 7. Update the item
    item_update = {"title": "Updated Item"}
    update_item_response = client.put(f"/api/v1/items/{item_id}", json_data=item_update)
    assert update_item_response.status_code == 200, f"Update item failed: {update_item_response.text}"
    assert update_item_response.json()["title"] == item_update["title"]
    
    # 8. Delete the item
    delete_item_response = client.delete(f"/api/v1/items/{item_id}")
    assert delete_item_response.status_code == 200, f"Delete item failed: {delete_item_response.text}"
    
    # 9. Change user password
    password_data = {
        "current_password": signup_data["password"],
        "new_password": "newpassword123"
    }
    password_response = client.patch("/api/v1/users/me/password", json_data=password_data)
    assert password_response.status_code == 200, f"Password change failed: {password_response.text}"
    
    # 10. Verify login with new password works
    # Create a new client to avoid using the existing token
    new_client = BlackboxClient(base_url=client.base_url)
    new_login_response = new_client.login(
        email=signup_data["email"],
        password="newpassword123"
    )
    assert new_login_response.status_code == 200, f"Login with new password failed: {new_login_response.text}"
    
    # 11. Delete user account
    # Use the original client which has the token
    delete_response = client.delete("/api/v1/users/me")
    assert delete_response.status_code == 200, f"Delete user failed: {delete_response.text}"
    
    # 12. Verify user account is deleted (attempt login)
    failed_login_client = BlackboxClient(base_url=client.base_url)
    failed_login_response = failed_login_client.login(
        email=signup_data["email"],
        password="newpassword123"
    )
    assert failed_login_response.status_code != 200, "Login should fail for deleted user"


def test_admin_user_management(admin_client, client):
    """Test the admin capabilities for user management."""
    # Skip if admin client wasn't created successfully
    if not admin_client.token:
        pytest.skip("Admin client not available (login failed)")
        
    # 1. Admin creates a new user
    new_user_data = {
        "email": f"admintest-{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "full_name": "Admin Created User",
        "is_superuser": False
    }
    create_response = admin_client.post("/api/v1/users/", json_data=new_user_data)
    assert create_response.status_code == 200, f"Admin create user failed: {create_response.text}"
    new_user = create_response.json()
    user_id = new_user["id"]
    assert_uuid_format(user_id)
    
    # 2. Admin gets user by ID
    get_response = admin_client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200, f"Admin get user failed: {get_response.text}"
    assert get_response.json()["email"] == new_user_data["email"]
    
    # 3. Admin updates user
    update_data = {"full_name": "Updated By Admin", "is_superuser": True}
    update_response = admin_client.patch(f"/api/v1/users/{user_id}", json_data=update_data)
    assert update_response.status_code == 200, f"Admin update user failed: {update_response.text}"
    updated_user = update_response.json()
    assert updated_user["full_name"] == update_data["full_name"]
    assert updated_user["is_superuser"] == update_data["is_superuser"]
    
    # 4. Admin lists all users
    list_response = admin_client.get("/api/v1/users/")
    assert list_response.status_code == 200, f"Admin list users failed: {list_response.text}"
    users = list_response.json()
    assert "data" in users
    assert "count" in users
    assert isinstance(users["data"], list)
    assert len(users["data"]) >= 1
    
    # 5. Admin deletes user
    delete_response = admin_client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 200, f"Admin delete user failed: {delete_response.text}"
    
    # 6. Verify user is deleted
    get_deleted_response = admin_client.get(f"/api/v1/users/{user_id}")
    assert get_deleted_response.status_code == 404, "Deleted user should not be accessible"
    
    # 7. Verify regular user can't access admin endpoints
    # Create a regular user
    regular_client = BlackboxClient(base_url=client.base_url)
    user_data = regular_client.create_and_login_user()
    
    # Try to list all users (admin-only endpoint)
    regular_list_response = regular_client.get("/api/v1/users/")
    assert regular_list_response.status_code in (401, 403, 404), \
        "Regular user should not access admin endpoints"