from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from kila_models.models.base import SubscriptionTier, SubscriptionStatus


class SubscriptionResponse(BaseModel):
    """Subscription/tier data for the current user"""
    tier: SubscriptionTier
    status: SubscriptionStatus
    trial_expires_at: Optional[datetime] = None
    is_super_user: bool = False

    model_config = ConfigDict(from_attributes=True)


class ProfileSetupRequest(BaseModel):
    """Request schema for setting up user profile"""
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name (required)")
    middle_name: Optional[str] = Field(None, max_length=100, description="User's middle name (optional)")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name (required)")
    phone: Optional[str] = Field(None, max_length=100, description="User's phone number (optional)")
    email: EmailStr = Field(..., description="User's email address (required)")
    company_name: str = Field(..., min_length=1, max_length=100, description="Company name (required)")
    job_title: Optional[str] = Field(None, max_length=100, description="User's job title (optional)")


class CompanyResponse(BaseModel):
    """Response schema for company data"""
    company_id: str
    company_name: str

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    """Response schema for user profile data"""
    user_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[CompanyResponse] = None
    subscription: Optional[SubscriptionResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompanySearchResult(BaseModel):
    """Response schema for company search results"""
    company_id: str
    company_name: str

    model_config = ConfigDict(from_attributes=True)
