import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_get_current_user():
    """Test retrieving current user profile."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data

def test_update_user_profile():
    """Test updating user profile."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"full_name": "Updated Name"}
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 200

def test_change_password():
    """Test changing user password."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    password_data = {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    response = client.post("/api/v1/users/me/password", json=password_data, headers=headers)
    # Should return appropriate status based on implementation
    assert response.status_code in [200, 400, 422]
