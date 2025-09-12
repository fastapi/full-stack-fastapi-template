from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.constants import (
    BAD_REQUEST_CODE,
    NOT_FOUND_CODE,
    OK_CODE,
)
from app.core.config import settings
from app.core.security import verify_password
from app.crud import create_user
from app.models import UserCreate
from app.tests.utils.user import user_authentication_headers
from app.tests.utils.test_helpers import random_email, random_lower_string
from app.email_utils import generate_password_reset_token


def _create_test_user_with_credentials(db: Session):
    """Create a test user and return user data and credentials."""
    email = random_email()
    password = random_lower_string()
    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    return user, email, password


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    response_data = response.json()
    assert response.status_code == OK_CODE
    assert "access_token" in response_data
    assert response_data["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert response.status_code == BAD_REQUEST_CODE


def test_use_access_token(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    response_data = response.json()
    assert response.status_code == OK_CODE
    assert "email" in response_data


def test_recovery_password(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        email = "test@example.com"
        response = client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert response.status_code == OK_CODE
        assert response.json() == {"message": "Password recovery email sent"}


def test_recovery_password_user_not_exits(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    email = "jVgQr@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == NOT_FOUND_CODE


def test_reset_password(client: TestClient, db: Session) -> None:
    user, email, password = _create_test_user_with_credentials(db)
    new_password = random_lower_string()
    
    token = generate_password_reset_token(email=email)
    headers = user_authentication_headers(client=client, email=email, password=password)
    reset_data = {"new_password": new_password, "token": token}

    response = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=reset_data,
    )

    assert response.status_code == OK_CODE
    assert response.json() == {"message": "Password updated successfully"}

    db.refresh(user)
    assert verify_password(new_password, user.hashed_password)


def test_reset_password_invalid_token(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    reset_data = {"new_password": "changethis", "token": "invalid"}
    response = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=reset_data,
    )
    response_content = response.json()

    assert "detail" in response_content
    assert response.status_code == BAD_REQUEST_CODE
    assert response_content["detail"] == "Invalid token"
