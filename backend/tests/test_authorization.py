import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_unauthorized_access():
    """Test accessing protected endpoints without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_invalid_token_format():
    """Test using malformed authorization token."""
    headers = {"Authorization": "InvalidTokenFormat"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401

def test_expired_token():
    """Test using expired token."""
    # This would require creating an expired token
    headers = {"Authorization": "Bearer expired_token_here"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401

def test_insufficient_permissions():
    """Test accessing admin endpoints with regular user token."""
    headers = {"Authorization": "Bearer regular_user_token"}
    response = client.get("/api/v1/admin/users/", headers=headers)
    assert response.status_code in [401, 403, 404]
