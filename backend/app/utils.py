import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import emails  # type: ignore
import jwt
from jinja2 import Template

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
) -> None:
    """Send email with subject and HTML content."""
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logging.info(f"Email sent to {email_to}, response: {response.status_code}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = f"""
    <html>
        <body>
            <h1>Test Email from {project_name}</h1>
            <p>This is a test email sent to {email_to}</p>
        </body>
    </html>
    """
    send_email(email_to=email_to, subject=subject, html_content=html_content)


def generate_test_email(email_to: str) -> EmailData:
    """Generate test email data."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = f"""
    <html>
        <body>
            <h1>Test Email from {project_name}</h1>
            <p>This is a test email sent to {email_to}</p>
        </body>
    </html>
    """
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """Generate reset password email data."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    html_content = f"""
    <html>
        <body>
            <h1>Password Recovery for {project_name}</h1>
            <p>Hello {email},</p>
            <p>You have requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{link}">Reset Password</a></p>
            <p>This link will expire in {settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS} hours.</p>
            <p>If you did not request this, please ignore this email.</p>
        </body>
    </html>
    """
    return EmailData(html_content=html_content, subject=subject)


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """Send reset password email."""
    email_data = generate_reset_password_email(email_to=email_to, email=email, token=token)
    send_email(email_to=email_to, subject=email_data.subject, html_content=email_data.html_content)


def generate_new_account_email(email_to: str, username: str, password: str) -> EmailData:
    """Generate new account email data."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    link = settings.SERVER_HOST
    html_content = f"""
    <html>
        <body>
            <h1>Welcome to {project_name}</h1>
            <p>Hello {username},</p>
            <p>Your account has been created successfully!</p>
            <p>Email: {email_to}</p>
            <p>Password: {password}</p>
            <p>You can login at: <a href="{link}">{link}</a></p>
            <p>Please change your password after your first login.</p>
        </body>
    </html>
    """
    return EmailData(html_content=html_content, subject=subject)


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    """Send new account email."""
    email_data = generate_new_account_email(email_to=email_to, username=username, password=password)
    send_email(email_to=email_to, subject=email_data.subject, html_content=email_data.html_content)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def get_file_hash(content: bytes) -> str:
    """Generate a unique hash for file content."""
    return hashlib.sha256(content).hexdigest()[:16]  # Using first 16 chars for shorter filenames
