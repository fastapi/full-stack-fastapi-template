import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails  # type: ignore
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings


@dataclass
class EmailData:
    """
    Class for email data.
    """

    html_content: str  # The HTML content of the email
    subject: str  # The subject line of the email


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """
    Render an email template.

    This function reads an email template file, renders it with the provided context,
    and returns the resulting HTML content.

    Args:
        template_name (str): The name of the template file to render.
        context (dict[str, Any]): A dictionary containing the context data for rendering the template.

    Returns:
        str: The rendered HTML content of the email.

    Raises:
        FileNotFoundError: If the specified template file is not found.
        jinja2.exceptions.TemplateError: If there's an error in rendering the template.

    Notes:
        The template files are expected to be located in the 'email-templates/build' directory
        relative to the current file's location.
    """
    # Construct the path to the email template file
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    # Render the template with the provided context
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """
    Send an email.

    This function sends an email using the configured SMTP settings.

    Args:
        email_to (str): The recipient's email address.
        subject (str, optional): The subject of the email. Defaults to an empty string.
        html_content (str, optional): The HTML content of the email. Defaults to an empty string.

    Returns:
        None

    Raises:
        AssertionError: If email functionality is not enabled in the settings.
        SMTPException: If there's an error in sending the email.

    Notes:
        This function relies on the 'emails' library and the application's settings
        for SMTP configuration.
    """
    # Ensure email functionality is enabled in settings
    assert settings.emails_enabled, "no provided configuration for email variables"

    # Create an email message object with subject, content, and sender information
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    # Configure SMTP options based on settings
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    # Send the email using the configured SMTP options and log the result
    response = message.send(to=email_to, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    """
    Generate a test email.

    This function creates a test email with a predefined subject and content.

    Args:
        email_to (str): The recipient's email address.

    Returns:
        EmailData: An object containing the HTML content and subject of the test email.

    Notes:
        The email content is generated using a template named 'test_email.html'.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    # Render the test email template with project name and recipient email
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """
    Generate a reset password email.

    This function creates an email for password reset with a link containing a reset token.

    Args:
        email_to (str): The recipient's email address.
        email (str): The user's email address (may be different from email_to).
        token (str): The password reset token.

    Returns:
        EmailData: An object containing the HTML content and subject of the reset password email.

    Notes:
        The email content is generated using a template named 'reset_password.html'.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    # Construct the reset password link with the provided token
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    # Render the reset password email template with necessary context
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    """
    Generate a new account email.

    This function creates an email for a newly created account with login credentials.

    Args:
        email_to (str): The recipient's email address.
        username (str): The username for the new account.
        password (str): The password for the new account.

    Returns:
        EmailData: An object containing the HTML content and subject of the new account email.

    Notes:
        The email content is generated using a template named 'new_account.html'.
        Sending passwords via email is generally not recommended for security reasons.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    # Render the new account email template with account details
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.

    This function creates a JWT token for password reset purposes.

    Args:
        email (str): The email address of the user requesting a password reset.

    Returns:
        str: A JWT token encoded as a string.

    Notes:
        The token includes expiration time, not-before time, and the user's email as subject.
        The token is signed using the application's SECRET_KEY.
    """
    # Calculate token expiration time
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    # Encode the JWT token with expiration, not-before, and subject claims
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token.

    This function decodes and verifies a JWT token used for password reset.

    Args:
        token (str): The JWT token to verify.

    Returns:
        str | None: The email address (subject) from the token if valid, None otherwise.

    Raises:
        jwt.exceptions.InvalidTokenError: If the token is invalid or expired.

    Notes:
        The token is verified using the application's SECRET_KEY.
    """
    try:
        # Attempt to decode and verify the JWT token
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        # Return None if the token is invalid
        return None
