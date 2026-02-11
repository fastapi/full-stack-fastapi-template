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


class ProjectCreateRequest(BaseModel):
    """
    Request schema for creating a new project.

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
