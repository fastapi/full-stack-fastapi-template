import logging
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.crud import create_user
from app.models import User, UserCreate
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_recovery_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        email = "test@example.com"
        r = client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {
            "message": "If that email is registered, we sent a password recovery link"
        }


def test_recovery_password_user_not_exits(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    email = "jVgQr@example.com"
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    # Should return 200 with generic message to prevent email enumeration attacks
    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }


def test_recovery_password_with_disabled_email_skips_user_lookup_and_email(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    email = random_email()

    with caplog.at_level(logging.WARNING, logger="app.api.routes.login"):
        with (
            patch("app.api.routes.login.crud.get_user_by_email") as get_user_mock,
            patch("app.core.config.settings.SMTP_HOST", None),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", None),
            patch("app.api.routes.login.generate_password_reset_token") as token_mock,
            patch("app.api.routes.login.generate_reset_password_email") as email_mock,
            patch("app.api.routes.login.send_email") as send_email_mock,
        ):
            r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")

    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }
    get_user_mock.assert_not_called()
    token_mock.assert_not_called()
    email_mock.assert_not_called()
    send_email_mock.assert_not_called()
    assert "email delivery is disabled" in caplog.text
    assert email not in caplog.text


def test_recovery_password_with_existing_user_and_email_enabled(
    client: TestClient,
) -> None:
    email = random_email()
    user = User(
        email=email,
        hashed_password="not-used",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    email_data = SimpleNamespace(
        subject="Reset password",
        html_content="<p>reset-password</p>",
    )

    with (
        patch("app.api.routes.login.crud.get_user_by_email", return_value=user),
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com"),
        patch(
            "app.api.routes.login.generate_password_reset_token",
            return_value="reset-token",
        ) as token_mock,
        patch(
            "app.api.routes.login.generate_reset_password_email",
            return_value=email_data,
        ) as email_mock,
        patch("app.api.routes.login.send_email") as send_email_mock,
    ):
        r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")

    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }
    token_mock.assert_called_once_with(email=email)
    email_mock.assert_called_once_with(
        email_to=user.email,
        email=email,
        token="reset-token",
    )
    send_email_mock.assert_called_once_with(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


def test_recovery_password_with_email_failure_returns_generic_response(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    email = random_email()
    user = User(
        email=email,
        hashed_password="not-used",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    with caplog.at_level(logging.ERROR, logger="app.api.routes.login"):
        with (
            patch("app.api.routes.login.crud.get_user_by_email", return_value=user),
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com"),
            patch(
                "app.api.routes.login.send_email",
                side_effect=RuntimeError("SMTP unavailable"),
            ) as send_email_mock,
        ):
            r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")

    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }
    send_email_mock.assert_called_once()
    assert caplog.text == ""


def test_recovery_password_with_email_template_failure_returns_generic_response(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    email = random_email()
    user = User(
        email=email,
        hashed_password="not-used",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    with caplog.at_level(logging.ERROR, logger="app.api.routes.login"):
        with (
            patch("app.api.routes.login.crud.get_user_by_email", return_value=user),
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com"),
            patch(
                "app.api.routes.login.generate_password_reset_token",
                return_value="reset-token",
            ) as token_mock,
            patch(
                "app.api.routes.login.generate_reset_password_email",
                side_effect=RuntimeError("template unavailable"),
            ) as email_mock,
            patch("app.api.routes.login.send_email") as send_email_mock,
        ):
            r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}")

    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }
    token_mock.assert_called_once_with(email=email)
    email_mock.assert_called_once_with(
        email_to=user.email,
        email=email,
        token="reset-token",
    )
    send_email_mock.assert_not_called()
    assert caplog.text == ""


def test_reset_password(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(email=email)
    headers = user_authentication_headers(client=client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    db.refresh(user)
    verified, _ = verify_password(new_password, user.hashed_password)
    assert verified


def test_reset_password_invalid_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


def test_login_with_bcrypt_password_upgrades_to_argon2(
    client: TestClient, db: Session
) -> None:
    """Test that logging in with a bcrypt password hash upgrades it to argon2."""
    email = random_email()
    password = random_lower_string()

    # Create a bcrypt hash directly (simulating legacy password)
    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")  # bcrypt hashes start with $2

    user = User(email=email, hashed_password=bcrypt_hash, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.hashed_password.startswith("$2")

    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens

    db.refresh(user)

    # Verify the hash was upgraded to argon2
    assert user.hashed_password.startswith("$argon2")

    verified, updated_hash = verify_password(password, user.hashed_password)
    assert verified
    # Should not need another update since it's already argon2
    assert updated_hash is None


def test_login_with_argon2_password_keeps_hash(client: TestClient, db: Session) -> None:
    """Test that logging in with an argon2 password hash does not update it."""
    email = random_email()
    password = random_lower_string()

    # Create an argon2 hash (current default)
    argon2_hash = get_password_hash(password)
    assert argon2_hash.startswith("$argon2")

    # Create user with argon2 hash
    user = User(email=email, hashed_password=argon2_hash, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    original_hash = user.hashed_password

    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens

    db.refresh(user)

    assert user.hashed_password == original_hash
    assert user.hashed_password.startswith("$argon2")
