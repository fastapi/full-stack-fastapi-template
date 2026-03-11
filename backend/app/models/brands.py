"""
Brands Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SegmentData(BaseModel):
    segment_name: str = Field(..., min_length=1, max_length=100)
    prompts: str = Field(..., min_length=1)
    model_config = ConfigDict(from_attributes=True)


class SegmentDetail(BaseModel):
    prompt_id: str
    segment_name: str
    prompts: str
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class BrandResponse(BaseModel):
    brand_id: str
    brand_name: str
    description: Optional[str] = None
    company_id: Optional[str] = None
    created_by: str
    created_at: datetime
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class BrandListResponse(BaseModel):
    brands: list[BrandResponse] = Field(default_factory=list)
    total_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class BrandDetailResponse(BaseModel):
    brand_id: str
    brand_name: str
    description: Optional[str] = None
    company_id: Optional[str] = None
    created_by: str
    created_at: datetime
    is_active: bool = True
    segments: list[SegmentDetail] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class BrandSetupRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    segments: list[SegmentData] = Field(..., min_length=1, max_length=3)
    model_config = ConfigDict(from_attributes=True)


class BrandSetupResponse(BaseModel):
    brand_id: str
    prompt_count: int = 0
    message: str = "Brand setup completed successfully"
    model_config = ConfigDict(from_attributes=True)


class BrandUpdateRequest(BaseModel):
    brand_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class BrandUpdateResponse(BaseModel):
    brand_id: str
    message: str = "Brand updated successfully"
    model_config = ConfigDict(from_attributes=True)


class BrandFullUpdateRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    segments: list[SegmentData] = Field(..., min_length=1, max_length=3)
    model_config = ConfigDict(from_attributes=True)


class BrandMemberRequest(BaseModel):
    user_id: str = Field(..., description="User ID to grant access to")
    user_role: str = Field("monitor", description="Role: 'owner' or 'monitor'")
    model_config = ConfigDict(from_attributes=True)


class BrandMemberResponse(BaseModel):
    brand_id: str
    user_id: str
    user_role: str
    message: str = "Member added successfully"
    model_config = ConfigDict(from_attributes=True)
