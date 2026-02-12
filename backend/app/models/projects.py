"""
Projects Pydantic schemas for API request/response models.

This module defines the data transfer objects (DTOs) used by the projects API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectResponse(BaseModel):
    """
    Response schema for a single project.

    Attributes:
        project_id: Unique identifier for the project
        project_name: Display name of the project
        description: Project description (optional)
        company_id: Associated company ID (optional)
        created_by: User ID who created the project
        created_at: Timestamp when the project was created
        is_active: Whether the project is currently active
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    project_name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    created_by: str = Field(..., description="User ID who created the project")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(True, description="Whether the project is active")

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """
    Response schema for a list of projects.

    Attributes:
        projects: List of project objects
        total_count: Total number of projects
    """
    projects: list[ProjectResponse] = Field(default_factory=list, description="List of projects")
    total_count: int = Field(0, description="Total number of projects")

    model_config = ConfigDict(from_attributes=True)


class SegmentData(BaseModel):
    """
    Schema for a single segment with prompts.

    Attributes:
        segment_name: Name of the market segment
        prompts: AI search prompts for this segment
    """
    segment_name: str = Field(..., min_length=1, max_length=100, description="Segment name")
    prompts: str = Field(..., min_length=1, description="Prompts for AI search")

    model_config = ConfigDict(from_attributes=True)


class ProjectSetupRequest(BaseModel):
    """
    Request schema for complete project setup including brand and prompts.

    This request creates:
    1. A new project record
    2. A brand record (if not exists)
    3. Brand prompt records for each segment

    Attributes:
        project_name: Name of the project
        project_description: Optional project description
        brand_name: Name of the brand to monitor
        segments: List of segments with their prompts (1-3 segments)
    """
    project_name: str = Field(..., min_length=1, max_length=100, description="Project name")
    project_description: Optional[str] = Field(None, max_length=255, description="Project description")
    brand_name: str = Field(..., min_length=1, max_length=100, description="Brand name to monitor")
    segments: list[SegmentData] = Field(..., min_length=1, max_length=3, description="Segments with prompts")

    model_config = ConfigDict(from_attributes=True)


class ProjectSetupResponse(BaseModel):
    """
    Response schema after complete project setup.

    Attributes:
        project_id: The newly created project's ID
        brand_id: The brand ID (existing or newly created)
        prompt_count: Number of prompts created
        message: Success message
    """
    project_id: str = Field(..., description="Newly created project ID")
    brand_id: str = Field(..., description="Brand ID (new or existing)")
    prompt_count: int = Field(0, description="Number of prompts created")
    message: str = Field("Project setup completed successfully", description="Success message")

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateRequest(BaseModel):
    """
    Request schema for creating a new project (simple version).

    Attributes:
        project_name: Name of the project (required)
        description: Project description (optional)
        company_id: Associated company ID (optional)
    """
    project_name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    company_id: Optional[str] = Field(None, description="Associated company ID")

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateResponse(BaseModel):
    """
    Response schema after creating a new project.

    Attributes:
        project_id: The newly created project's ID
        message: Success message
    """
    project_id: str = Field(..., description="Newly created project ID")
    message: str = Field("Project created successfully", description="Success message")

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdateRequest(BaseModel):
    """
    Request schema for updating an existing project.

    All fields are optional - only provided fields will be updated.

    Attributes:
        project_name: New project name (optional)
        description: New project description (optional)
        is_active: New active status (optional)
    """
    project_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    is_active: Optional[bool] = Field(None, description="Whether the project is active")

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdateResponse(BaseModel):
    """
    Response schema after updating a project.

    Attributes:
        project_id: The updated project's ID
        message: Success message
    """
    project_id: str = Field(..., description="Updated project ID")
    message: str = Field("Project updated successfully", description="Success message")

    model_config = ConfigDict(from_attributes=True)


class SegmentDetail(BaseModel):
    """
    Schema for a segment with full details from BrandPromptTable.

    Attributes:
        prompt_id: Unique identifier for the prompt record
        segment_name: Name of the market segment
        prompts: AI search prompts for this segment
        is_active: Whether this prompt is active
    """
    prompt_id: str = Field(..., description="Prompt record ID")
    segment_name: str = Field(..., description="Segment name")
    prompts: str = Field(..., description="Prompts for AI search")
    is_active: bool = Field(True, description="Whether this prompt is active")

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(BaseModel):
    """
    Response schema for project details including brand and prompts.

    Attributes:
        project_id: Unique identifier for the project
        project_name: Display name of the project
        description: Project description (optional)
        company_id: Associated company ID (optional)
        created_by: User ID who created the project
        created_at: Timestamp when the project was created
        is_active: Whether the project is currently active
        brand_id: The brand ID associated with this project
        brand_name: The brand name associated with this project
        segments: List of segments with their prompts
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    project_name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    created_by: str = Field(..., description="User ID who created the project")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(True, description="Whether the project is active")
    brand_id: Optional[str] = Field(None, description="Brand ID")
    brand_name: Optional[str] = Field(None, description="Brand name")
    segments: list[SegmentDetail] = Field(default_factory=list, description="Segments with prompts")

    model_config = ConfigDict(from_attributes=True)


class ProjectFullUpdateRequest(BaseModel):
    """
    Request schema for full project update including brand and prompts.

    Attributes:
        project_name: Name of the project
        project_description: Optional project description
        is_active: Whether the project is active
        brand_name: Name of the brand to monitor
        segments: List of segments with their prompts (1-3 segments)
    """
    project_name: str = Field(..., min_length=1, max_length=100, description="Project name")
    project_description: Optional[str] = Field(None, max_length=255, description="Project description")
    is_active: bool = Field(True, description="Whether the project is active")
    brand_name: str = Field(..., min_length=1, max_length=100, description="Brand name to monitor")
    segments: list[SegmentData] = Field(..., min_length=1, max_length=3, description="Segments with prompts")

    model_config = ConfigDict(from_attributes=True)
