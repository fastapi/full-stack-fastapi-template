import pytest
from unittest.mock import patch, MagicMock
from app.core.security import create_access_token, verify_password, get_password_hash

def test_create_access_token():
    """Test JWT token creation."""
    token = create_access_token(subject="test@example.com")
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_password_correct():
    """Test password verification with correct password."""
    plain_password = "testpassword"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True

def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    plain_password = "testpassword"
    hashed_password = get_password_hash(plain_password)
    assert verify_password("wrongpassword", hashed_password) is False

def test_get_password_hash():
    """Test password hashing."""
    password = "testpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 0
