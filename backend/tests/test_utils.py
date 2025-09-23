import pytest
from unittest.mock import Mock, patch
from app.utils import send_email, generate_password_reset_token, verify_password_reset_token

def test_generate_password_reset_token():
    """Test password reset token generation."""
    email = "test@example.com"
    token = generate_password_reset_token(email)
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_password_reset_token_valid():
    """Test verifying a valid password reset token."""
    email = "test@example.com"
    token = generate_password_reset_token(email)
    verified_email = verify_password_reset_token(token)
    assert verified_email == email

def test_verify_password_reset_token_invalid():
    """Test verifying an invalid password reset token."""
    invalid_token = "invalid_token_string"
    verified_email = verify_password_reset_token(invalid_token)
    assert verified_email is None

@patch('app.utils.emails.send_email')
def test_send_email_mock(mock_send_email):
    """Test email sending with mock."""
    mock_send_email.return_value = True
    result = send_email("test@example.com", "Test Subject", {"message": "Test"})
    assert result is True
    mock_send_email.assert_called_once()
