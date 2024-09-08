import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import resend
from jinja2 import Template

from app.core.config import settings


@dataclass
class EmailData:
    html_content: str
    subject: str

resend.api_key = settings.RESEND_API_KEY

def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    params: resend.Emails.SendParams = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [email_to],
        "subject": subject,
        "html": html_content
    }
    email: resend.Email = resend.Emails.send(params)
    logging.info(f"send email result: {email}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, token: str, username: str | None) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {username}"
    link = f"{settings.FRONTEND_SERVER_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "reset_link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.server_host,
        },
    )
    return EmailData(html_content=html_content, subject=subject)

def generate_new_account_email_otp(
    email_to: str, username: str, otp: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="otp.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "otp": otp,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
