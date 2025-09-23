import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_valid_credentials():
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "invalid@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400

def test_protected_route_without_token():
    """Test accessing protected route without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
