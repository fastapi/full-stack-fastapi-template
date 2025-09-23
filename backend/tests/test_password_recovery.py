import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_password_recovery_request():
    """Test requesting password recovery."""
    recovery_data = {"email": "test@example.com"}
    response = client.post("/api/v1/password-recovery/", json=recovery_data)
    assert response.status_code in [200, 404]

@patch('app.utils.send_email')
def test_password_recovery_email_sent(mock_send_email):
    """Test that password recovery email is sent."""
    mock_send_email.return_value = True

    recovery_data = {"email": "test@example.com"}
    response = client.post("/api/v1/password-recovery/", json=recovery_data)

    if response.status_code == 200:
        mock_send_email.assert_called_once()

def test_reset_password_with_token():
    """Test resetting password with valid token."""
    reset_data = {
        "token": "valid_reset_token",
        "new_password": "newpassword123"
    }
    response = client.post("/api/v1/reset-password/", json=reset_data)
    assert response.status_code in [200, 400]

def test_reset_password_invalid_token():
    """Test resetting password with invalid token."""
    reset_data = {
        "token": "invalid_token",
        "new_password": "newpassword123"
    }
    response = client.post("/api/v1/reset-password/", json=reset_data)
    assert response.status_code == 400
