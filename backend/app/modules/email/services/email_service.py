"""
Email service.

This module provides business logic for email operations.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import emails  # type: ignore
from jinja2 import Template
from pydantic import EmailStr

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.email.domain.models import (
    EmailContent,
    EmailRequest,
    EmailTemplateType,
    TemplateData,
)

# Configure logger
logger = get_logger("email_service")


class EmailService:
    """
    Service for email operations.
    
    This class provides business logic for email operations.
    """
    
    def __init__(self):
        """Initialize email service."""
        self.templates_dir = Path(__file__).parents[3] / "email-templates" / "build"
        self.enabled = settings.emails_enabled
        self.smtp_options = self._get_smtp_options()
        self.from_name = settings.EMAILS_FROM_NAME
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.frontend_host = settings.FRONTEND_HOST
        self.project_name = settings.PROJECT_NAME
    
    def _get_smtp_options(self) -> Dict[str, Any]:
        """
        Get SMTP options from settings.
        
        Returns:
            Dictionary of SMTP options
        """
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        elif settings.SMTP_SSL:
            smtp_options["ssl"] = True
            
        if settings.SMTP_USER:
            smtp_options["user"] = settings.SMTP_USER
            
        if settings.SMTP_PASSWORD:
            smtp_options["password"] = settings.SMTP_PASSWORD
            
        return smtp_options
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template.
        
        Args:
            template_name: Template filename
            context: Template context variables
            
        Returns:
            Rendered HTML content
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            logger.error(f"Email template not found: {template_path}")
            raise ValueError(f"Email template not found: {template_name}")
        
        template_str = template_path.read_text()
        html_content = Template(template_str).render(context)
        
        return html_content
    
    def send_email(self, email_request: EmailRequest) -> bool:
        """
        Send an email.
        
        Args:
            email_request: Email request data
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email sending is disabled. Check your configuration.")
            return False
        
        try:
            message = emails.Message(
                subject=email_request.subject,
                html=email_request.html_content,
                text=email_request.plain_text_content,
                mail_from=(self.from_name, self.from_email),
            )
            
            # Add CC and BCC if provided
            if email_request.cc:
                message.cc = email_request.cc
                
            if email_request.bcc:
                message.bcc = email_request.bcc
                
            # Add reply-to if provided
            if email_request.reply_to:
                message.set_header("Reply-To", email_request.reply_to)
            
            # Add attachments if provided
            if email_request.attachments:
                for attachment_path in email_request.attachments:
                    message.attach(filename=attachment_path)
            
            # Send to each recipient
            for recipient in email_request.email_to:
                response = message.send(to=recipient, smtp=self.smtp_options)
                logger.info(f"Send email result to {recipient}: {response}")
                
                if not response.success:
                    logger.error(f"Failed to send email to {recipient}: {response.error}")
                    return False
            
            return True
        except Exception as e:
            logger.exception(f"Error sending email: {e}")
            return False
    
    def send_template_email(self, template_data: TemplateData) -> bool:
        """
        Send an email using a template.
        
        Args:
            template_data: Template data
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        template_content = self.get_template_content(template_data)
        
        email_request = EmailRequest(
            email_to=[template_data.email_to],
            subject=template_data.subject_override or template_content.subject,
            html_content=template_content.html_content,
            plain_text_content=template_content.plain_text_content,
        )
        
        return self.send_email(email_request)
    
    def get_template_content(self, template_data: TemplateData) -> EmailContent:
        """
        Get email content from a template.
        
        Args:
            template_data: Template data
            
        Returns:
            Email content
        """
        # Default context with project name
        context = {
            "project_name": self.project_name,
            "frontend_host": self.frontend_host,
            **template_data.context,
        }
        
        # Add email to context if not already present
        if "email" not in context:
            context["email"] = template_data.email_to
        
        template_filename = f"{template_data.template_type}.html"
        html_content = self._render_template(template_filename, context)
        
        # Generate subject based on template type
        subject = self._get_subject_for_template(
            template_data.template_type, context
        )
        
        return EmailContent(
            subject=subject,
            html_content=html_content,
        )
    
    def _get_subject_for_template(
        self, template_type: EmailTemplateType, context: Dict[str, Any]
    ) -> str:
        """
        Get subject for a template type.
        
        Args:
            template_type: Template type
            context: Template context
            
        Returns:
            Email subject
        """
        if template_type == EmailTemplateType.NEW_ACCOUNT:
            username = context.get("username", "")
            return f"{self.project_name} - New account for user {username}"
        
        elif template_type == EmailTemplateType.RESET_PASSWORD:
            username = context.get("username", "")
            return f"{self.project_name} - Password recovery for user {username}"
        
        elif template_type == EmailTemplateType.TEST_EMAIL:
            return f"{self.project_name} - Test email"
        
        else:  # Generic or custom
            return context.get("subject", f"{self.project_name} - Notification")
    
    # Specific email sending methods
    
    def send_test_email(self, email_to: EmailStr) -> bool:
        """
        Send a test email.
        
        Args:
            email_to: Recipient email address
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        template_data = TemplateData(
            template_type=EmailTemplateType.TEST_EMAIL,
            context={"email": email_to},
            email_to=email_to,
        )
        
        return self.send_template_email(template_data)
    
    def send_new_account_email(
        self, email_to: EmailStr, username: str, password: str
    ) -> bool:
        """
        Send a new account email.
        
        Args:
            email_to: Recipient email address
            username: Username
            password: Password
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        template_data = TemplateData(
            template_type=EmailTemplateType.NEW_ACCOUNT,
            context={
                "username": username,
                "password": password,
                "link": self.frontend_host,
            },
            email_to=email_to,
        )
        
        return self.send_template_email(template_data)
    
    def send_password_reset_email(
        self, email_to: EmailStr, username: str, token: str
    ) -> bool:
        """
        Send a password reset email.
        
        Args:
            email_to: Recipient email address
            username: Username
            token: Password reset token
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        link = f"{self.frontend_host}/reset-password?token={token}"
        
        template_data = TemplateData(
            template_type=EmailTemplateType.RESET_PASSWORD,
            context={
                "username": username,
                "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
                "link": link,
            },
            email_to=email_to,
        )
        
        return self.send_template_email(template_data)