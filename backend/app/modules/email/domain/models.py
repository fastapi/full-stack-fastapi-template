"""
Email domain models.

This module contains domain models related to email operations.
"""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel


class EmailTemplateType(str, Enum):
    """Types of email templates."""
    
    NEW_ACCOUNT = "new_account"
    RESET_PASSWORD = "reset_password"
    TEST_EMAIL = "test_email"
    GENERIC = "generic"


class EmailContent(SQLModel):
    """Email content model."""
    
    subject: str
    html_content: str
    plain_text_content: Optional[str] = None


class EmailRequest(SQLModel):
    """Email request model."""
    
    email_to: List[EmailStr]
    subject: str
    html_content: str
    plain_text_content: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    reply_to: Optional[EmailStr] = None
    attachments: Optional[List[str]] = None


class TemplateData(SQLModel):
    """Template data model for rendering email templates."""
    
    template_type: EmailTemplateType
    context: Dict[str, str]
    email_to: EmailStr
    subject_override: Optional[str] = None