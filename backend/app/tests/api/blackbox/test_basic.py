"""
Basic tests to verify the API server is running and responding to requests.

These tests simply check that the server is properly set up and responding
to basic requests as expected, without any complex authentication or business logic.
"""
import uuid
import pytest

from .client_utils import BlackboxClient

def test_server_is_running(client):
    """Test that the server is running and accessible."""
    # Use the docs endpoint to verify server is up
    response = client.get("/docs")
    assert response.status_code == 200
    
    # Should return HTML for the Swagger UI
    assert "text/html" in response.headers.get("content-type", "")

def test_public_endpoints(client):
    """Test that public endpoints are accessible without authentication."""
    # Test signup endpoint availability (without actually creating a user)
    # Just check that it returns the correct error for invalid data
    # rather than an authorization error
    response = client.post("/api/v1/users/signup", json_data={})
    
    # Should return validation error (422), not auth error (401/403)
    assert response.status_code == 422, \
        f"Expected validation error, got {response.status_code}: {response.text}"
        
    # Test login endpoint availability
    response = client.post("/api/v1/login/access-token", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    # Should return error (400 or 401), not "not found" or other error
    # Different FastAPI implementations may return 400 or 401 for invalid credentials
    assert response.status_code in (400, 401), \
        f"Expected authentication error, got {response.status_code}: {response.text}"

def test_auth_token_flow(client):
    """Test that the authentication flow works correctly using tokens."""
    # Create a random user
    unique_email = f"test-{uuid.uuid4()}@example.com"
    password = "testpassword123"
    
    # Sign up
    signup_response, user_credentials = client.sign_up(
        email=unique_email, 
        password=password,
        full_name="Test User"
    )
    
    assert signup_response.status_code == 200, \
        f"Signup failed: {signup_response.text}"
    
    # Login to get token
    login_response = client.login(unique_email, password)
    
    assert login_response.status_code == 200, \
        f"Login failed: {login_response.text}"
    
    token_data = login_response.json()
    assert "access_token" in token_data, \
        f"Login response missing access token: {token_data}"
    assert "token_type" in token_data, \
        f"Login response missing token type: {token_data}"
    assert token_data["token_type"].lower() == "bearer", \
        f"Expected bearer token, got: {token_data['token_type']}"
    
    # Test token by accessing a protected endpoint
    me_response = client.get("/api/v1/users/me")
    
    assert me_response.status_code == 200, \
        f"Access with token failed: {me_response.text}"
        
    me_data = me_response.json()
    assert me_data["email"] == unique_email, \
        f"User 'me' data has wrong email. Expected {unique_email}, got {me_data['email']}"

def test_item_creation(client):
    """Test that item creation and retrieval works correctly."""
    # Create a random user
    unique_email = f"test-{uuid.uuid4()}@example.com"
    password = "testpassword123"
    client.sign_up(email=unique_email, password=password)
    client.login(unique_email, password)
    
    # Create an item
    item_title = f"Test Item {uuid.uuid4().hex[:8]}"
    item_description = "This is a test item description"
    
    create_response = client.create_item(
        title=item_title, 
        description=item_description
    )
    
    assert create_response.status_code == 200, \
        f"Item creation failed: {create_response.text}"
    
    item_data = create_response.json()
    assert "id" in item_data, \
        f"Item creation response missing ID: {item_data}"
    assert item_data["title"] == item_title, \
        f"Item title mismatch. Expected {item_title}, got {item_data['title']}"
    assert item_data["description"] == item_description, \
        f"Item description mismatch. Expected {item_description}, got {item_data['description']}"
    
    # Get the item to verify
    item_id = item_data["id"]
    get_response = client.get(f"/api/v1/items/{item_id}")
    
    assert get_response.status_code == 200, \
        f"Item retrieval failed: {get_response.text}"
        
    get_item = get_response.json()
    assert get_item["id"] == item_id, \
        f"Item ID mismatch. Expected {item_id}, got {get_item['id']}"
    assert get_item["title"] == item_title, \
        f"Item title mismatch. Expected {item_title}, got {get_item['title']}"