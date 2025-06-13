"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import User, UserCreate
from app.tests.utils.test_client import TestClientWrapper, assert_successful_response, assert_error_response
from app.tests.utils.test_db import create_test_user
from app.tests.utils.utils import random_email, random_lower_string


def test_login_access_token(client: TestClient, db: Session):
    """Test login with access token."""
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    login_data = {
        "username": email,
        "password": password,
    }
    
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = assert_successful_response(response)
    
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_access_token_incorrect_password(client: TestClient, db: Session):
    """Test login with incorrect password."""
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    login_data = {
        "username": email,
        "password": "wrong-password",
    }
    
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert_error_response(response, status_code=400)


def test_login_access_token_user_not_exists(client: TestClient):
    """Test login with non-existent user."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": random_lower_string(),
    }
    
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert_error_response(response, status_code=400)


def test_use_access_token(test_client: TestClientWrapper, db: Session):
    """Test using the access token to access a protected endpoint."""
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Login and get token
    auth_headers = test_client.login(email, password)
    
    # Use token to access protected endpoint
    response = test_client.get("/users/me", headers=auth_headers)
    user_data = assert_successful_response(response)
    
    assert user_data["email"] == email
    assert user_data["id"] == str(user.id)


def test_signup_user(test_client: TestClientWrapper, db: Session):
    """Test user signup."""
    email = random_email()
    password = random_lower_string()
    full_name = "Test User"
    
    data = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    response = test_client.post("/users/signup", json=data)
    user_data = assert_successful_response(response)
    
    assert user_data["email"] == email
    assert user_data["full_name"] == full_name
    assert "id" in user_data
    
    # Verify user was created in the database
    from app.crud import get_user_by_email
    db_user = get_user_by_email(session=db, email=email)
    assert db_user is not None
    assert db_user.email == email
    assert db_user.full_name == full_name


def test_signup_user_existing_email(test_client: TestClientWrapper, db: Session):
    """Test signup with an existing email."""
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    data = {
        "email": email,
        "password": random_lower_string(),
        "full_name": "Another User"
    }
    
    response = test_client.post("/users/signup", json=data)
    assert_error_response(response, status_code=400)


def test_reset_password_request(test_client: TestClientWrapper, db: Session, monkeypatch):
    """Test password reset request."""
    # Mock the send_reset_password_email function
    email_sent = False
    
    def mock_send_email(*args, **kwargs):
        nonlocal email_sent
        email_sent = True
        return None
    
    monkeypatch.setattr("app.utils.send_email", mock_send_email)
    
    # Create a user
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Request password reset
    data = {"email": email}
    response = test_client.post("/password-recovery/", json=data)
    assert_successful_response(response)
    
    # Check that the email was "sent"
    assert email_sent


def test_reset_password_request_nonexistent_email(test_client: TestClientWrapper):
    """Test password reset request with non-existent email."""
    data = {"email": "nonexistent@example.com"}
    response = test_client.post("/password-recovery/", json=data)
    # Should still return 200 for security reasons (don't reveal if email exists)
    assert_successful_response(response)


def test_logout(test_client: TestClientWrapper, db: Session):
    """Test user logout functionality if implemented."""
    # This test is a placeholder for logout functionality
    # Implement if the API has a logout endpoint
    pass