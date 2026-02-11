"""
Projects API routes for managing user projects.

This module provides API endpoints for project management,
including listing, creating, and updating projects.

Endpoints:
    GET /projects - Get list of projects for the current user
    POST /projects - Create a new project
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging
import uuid

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.projects import (
    ProjectResponse,
    ProjectListResponse,
    ProjectCreateRequest,
    ProjectCreateResponse,
)
from kila_models.models import (
    UsersTable,
    ProjectsRecord,
)

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Create router with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve all projects for the current user.

    This endpoint queries the projects table filtered by the user's ID
    (created_by field). Results are ordered by created_at descending
    (newest first).

    Args:
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectListResponse with list of projects and total count

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching projects for user: {current_user.user_id}")

    # Build query to get projects for the current user, ordered by created_at desc
    query = (
        select(ProjectsRecord)
        .where(ProjectsRecord.created_by == current_user.user_id)
        .order_by(desc(ProjectsRecord.created_at))
    )

    # Execute query
    result = await db.execute(query)
    records = result.scalars().all()

    # Build response
    projects = [
        ProjectResponse(
            project_id=record.project_id,
            project_name=record.project_name,
            description=record.description,
            company_id=record.company_id,
            created_by=record.created_by,
            created_at=record.created_at,
            is_active=record.is_active
        )
        for record in records
    ]

    logger.info(f"Found {len(projects)} projects for user: {current_user.user_id}")

    return ProjectListResponse(
        projects=projects,
        total_count=len(projects)
    )


@router.post("", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Create a new project for the current user.

    This endpoint creates a new project record in the database
    with the current user as the creator.

    Args:
        project_data: Project creation request data
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectCreateResponse with the new project ID

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If project creation fails
    """
    logger.info(f"Creating new project for user: {current_user.user_id}, name: {project_data.project_name}")

    try:
        # Generate a unique project ID
        project_id = str(uuid.uuid4())

        # Create new project record
        new_project = ProjectsRecord(
            project_id=project_id,
            project_name=project_data.project_name,
            description=project_data.description,
            company_id=project_data.company_id,
            created_by=current_user.user_id,
            is_active=True
        )

        # Add to database
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)

        logger.info(f"Project created successfully: {project_id}")

        return ProjectCreateResponse(
            project_id=project_id,
            message="Project created successfully"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )
