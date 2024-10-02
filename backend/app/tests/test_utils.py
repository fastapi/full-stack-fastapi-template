from datetime import datetime, timezone
from unittest.mock import patch

import jwt
import pytest

from app.core.config import settings
from app.utils import (
    EmailData,
    generate_new_account_email,
    generate_password_reset_token,
    generate_reset_password_email,
    generate_test_email,
    send_email,
    verify_password_reset_token,
)


# Test the send_email function with different SMTP configurations
@pytest.mark.parametrize(
    "smtp_config",
    [
        {"SMTP_TLS": True, "SMTP_SSL": False},
        {"SMTP_TLS": False, "SMTP_SSL": True},
        {"SMTP_TLS": False, "SMTP_SSL": False},
    ],
)
def test_send_email(smtp_config: dict[str, bool]) -> None:
    """
    Test the send_email function with different SMTP configurations.

    This test verifies that the send_email function correctly sends an email
    using various SMTP configurations.

    Args:
        smtp_config (dict[str, bool]): A dictionary containing SMTP configuration options.

    Returns:
        None

    Raises:
        AssertionError: If the email message is not created or sent as expected.

    Notes:
        This test uses mocking to simulate different SMTP configurations and verify
        the behavior of the send_email function.
    """
    with (
        patch("app.utils.emails.Message") as mock_message,
        patch("app.utils.settings") as mock_settings,
    ):
        # Mock the settings for the email configuration
        mock_settings.emails_enabled = True
        mock_settings.SMTP_HOST = "localhost"
        mock_settings.SMTP_PORT = 25
        mock_settings.SMTP_USER = "user"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.EMAILS_FROM_NAME = "Test"
        mock_settings.EMAILS_FROM_EMAIL = "test@example.com"
        mock_settings.SMTP_TLS = smtp_config["SMTP_TLS"]
        mock_settings.SMTP_SSL = smtp_config["SMTP_SSL"]

        # Call the send_email function
        send_email(
            email_to="to@example.com", subject="Test", html_content="<p>Test</p>"
        )

        # Assert that the email message was created and sent
        mock_message.assert_called_once()
        mock_message.return_value.send.assert_called_once()


def test_generate_test_email() -> None:
    """
    Test the generate_test_email function.

    This test verifies that the generate_test_email function correctly generates
    an email with the expected properties.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the generated email does not have the expected properties.

    Notes:
        This test uses mocking to simulate the email template rendering process.
    """
    email_to = "test@example.com"
    with patch("app.utils.render_email_template") as mock_render:
        # Mock the email template rendering
        mock_render.return_value = "<p>Test Email</p>"
        result = generate_test_email(email_to)

    # Assert that the generated email has the correct properties
    assert isinstance(result, EmailData)
    assert result.subject == f"{settings.PROJECT_NAME} - Test email"
    assert result.html_content == "<p>Test Email</p>"


def test_generate_reset_password_email() -> None:
    """
    Test the generate_reset_password_email function.

    This test verifies that the generate_reset_password_email function correctly
    generates an email with the expected properties for password reset.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the generated email does not have the expected properties.

    Notes:
        This test uses mocking to simulate the email template rendering process.
    """
    email_to = "test@example.com"
    email = "user@example.com"
    token = "test_token"
    with patch("app.utils.render_email_template") as mock_render:
        # Mock the email template rendering
        mock_render.return_value = "<p>Reset Password</p>"
        result = generate_reset_password_email(email_to, email, token)

    # Assert that the generated email has the correct properties
    assert isinstance(result, EmailData)
    assert (
        result.subject
        == f"{settings.PROJECT_NAME} - Password recovery for user {email}"
    )
    assert result.html_content == "<p>Reset Password</p>"


def test_generate_new_account_email() -> None:
    """
    Test the generate_new_account_email function.

    This test verifies that the generate_new_account_email function correctly
    generates an email with the expected properties for a new account.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the generated email does not have the expected properties.

    Notes:
        This test uses mocking to simulate the email template rendering process.
    """
    email_to = "test@example.com"
    username = "testuser"
    password = "testpass"
    with patch("app.utils.render_email_template") as mock_render:
        # Mock the email template rendering
        mock_render.return_value = "<p>New Account</p>"
        result = generate_new_account_email(email_to, username, password)

    # Assert that the generated email has the correct properties
    assert isinstance(result, EmailData)
    assert (
        result.subject == f"{settings.PROJECT_NAME} - New account for user {username}"
    )
    assert result.html_content == "<p>New Account</p>"


def test_generate_password_reset_token() -> str:
    """
    Test the generate_password_reset_token function.

    This test verifies that the generate_password_reset_token function correctly
    generates a token for password reset.

    Args:
        None

    Returns:
        str: The generated token.

    Raises:
        AssertionError: If the generated token is not as expected.

    Notes:
        This test uses mocking to simulate the current datetime and JWT encoding process.
    """
    email = "test@example.com"
    with (
        patch("app.utils.datetime") as mock_datetime,
        patch("app.utils.jwt.encode") as mock_encode,
    ):
        # Mock the current datetime and JWT encoding
        mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_encode.return_value = "encoded_token"
        result = generate_password_reset_token(email)

    # Assert that the generated token is correct
    assert result == "encoded_token"
    return result


def test_verify_password_reset_token() -> None:
    """
    Test the verify_password_reset_token function.

    This test verifies that the verify_password_reset_token function correctly
    verifies a valid password reset token.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the verified email is not as expected.

    Notes:
        This test uses mocking to simulate the JWT decoding process.
    """
    token = "valid_token"
    with patch("app.utils.jwt.decode") as mock_decode:
        # Mock the JWT decoding
        mock_decode.return_value = {"sub": "test@example.com"}
        result = verify_password_reset_token(token)

    # Assert that the verified email is correct
    assert result == "test@example.com"


def test_verify_password_reset_token_invalid() -> None:
    """
    Test the verify_password_reset_token function with an invalid token.

    This test verifies that the verify_password_reset_token function correctly
    handles an invalid password reset token.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the result is not None for an invalid token.

    Notes:
        This test uses mocking to simulate the JWT decoding process raising an InvalidTokenError.
    """
    token = "invalid_token"
    with patch("app.utils.jwt.decode") as mock_decode:
        # Mock the JWT decoding to raise an InvalidTokenError
        mock_decode.side_effect = jwt.exceptions.InvalidTokenError
        result = verify_password_reset_token(token)

    # Assert that the result is None for an invalid token
    assert result is None
