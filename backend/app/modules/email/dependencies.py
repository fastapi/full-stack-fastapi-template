"""
Email module dependencies.

This module provides dependencies for the email module.
"""
from fastapi import Depends

from app.modules.email.services.email_service import EmailService


def get_email_service() -> EmailService:
    """
    Get an email service instance.
    
    Returns:
        Email service instance
    """
    return EmailService()