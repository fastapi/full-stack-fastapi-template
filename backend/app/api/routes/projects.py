"""
Projects API routes for managing user projects.

This module provides API endpoints for project management,
including listing, creating, updating projects with brand and prompt setup.

Endpoints:
    GET /projects - Get list of projects for the current user
    GET /projects/{project_id} - Get project details with brand and prompts
    POST /projects - Create a new project (simple)
    POST /projects/setup - Complete project setup with brand and prompts
    PATCH /projects/{project_id} - Update an existing project (simple)
    PUT /projects/{project_id} - Full update of project with brand and prompts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, delete
import logging
import uuid
from nanoid import generate as nanoid_generate

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.projects import (
    ProjectResponse,
    ProjectListResponse,
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectSetupRequest,
    ProjectSetupResponse,
    ProjectUpdateRequest,
    ProjectUpdateResponse,
    ProjectDetailResponse,
    ProjectFullUpdateRequest,
    SegmentDetail,
)
from kila_models.models import (
    UsersTable,
    UsersProfileTable,
    ProjectsRecord,
    ProjectUserTable,
    ProjectRole,
    BrandsTable,
    BrandPromptTable,
)

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Create router with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/projects", tags=["projects"])


def generate_id(prefix: str) -> str:
    """
    Generate a unique ID with a given prefix.

    Args:
        prefix: The prefix for the ID (e.g., "P_", "B_")

    Returns:
        A unique ID string with the prefix
    """
    return f"{prefix}{nanoid_generate(size=10)}"


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


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Get project details including brand and prompts.

    This endpoint retrieves the full project information including
    brand name and all segments/prompts from BrandPromptTable.

    Args:
        project_id: The project ID to retrieve
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectDetailResponse with full project details

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If project not found or user doesn't own it
    """
    logger.info(f"Fetching project details for: {project_id}, user: {current_user.user_id}")

    # Find the project and verify ownership
    project_query = select(ProjectsRecord).where(
        ProjectsRecord.project_id == project_id,
        ProjectsRecord.created_by == current_user.user_id
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        logger.warning(f"Project not found or access denied: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have permission to view it"
        )

    # Fetch brand prompts for this project
    prompts_query = select(BrandPromptTable).where(
        BrandPromptTable.project_id == project_id
    ).order_by(BrandPromptTable.id)
    prompts_result = await db.execute(prompts_query)
    prompts = prompts_result.scalars().all()

    # Extract brand info and segments from prompts
    brand_id = None
    brand_name = None
    segments = []

    for prompt in prompts:
        if brand_id is None:
            brand_id = prompt.brand_id
            brand_name = prompt.brand_name

        segments.append(SegmentDetail(
            prompt_id=prompt.prompt_id,
            segment_name=prompt.segment or "",
            prompts=prompt.prompt,
            is_active=prompt.is_active
        ))

    logger.info(f"Found project {project_id} with {len(segments)} segments")

    return ProjectDetailResponse(
        project_id=project.project_id,
        project_name=project.project_name,
        description=project.description,
        company_id=project.company_id,
        created_by=project.created_by,
        created_at=project.created_at,
        is_active=project.is_active,
        brand_id=brand_id,
        brand_name=brand_name,
        segments=segments
    )


@router.post("", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Create a new project for the current user (simple version).

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


@router.post("/setup", response_model=ProjectSetupResponse, status_code=status.HTTP_201_CREATED)
async def setup_project(
    setup_data: ProjectSetupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Complete project setup with brand and prompts.

    This endpoint performs the following operations:
    1. Creates a new project record
    2. Creates or retrieves the brand (case-insensitive match)
    3. Creates brand prompt records for each segment

    Args:
        setup_data: Complete project setup request data
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectSetupResponse with project ID, brand ID, and prompt count

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If setup fails
    """
    logger.info(
        f"Setting up project for user: {current_user.user_id}, "
        f"project: {setup_data.project_name}, brand: {setup_data.brand_name}"
    )

    try:
        # Get user's company_id from profile
        profile_query = select(UsersProfileTable).where(
            UsersProfileTable.user_id == current_user.user_id
        )
        profile_result = await db.execute(profile_query)
        user_profile = profile_result.scalar_one_or_none()

        company_id = user_profile.company_id if user_profile else None

        if not company_id:
            logger.warning(f"No company_id found for user: {current_user.user_id}")
            # Use a default or generate one
            company_id = f"company_{current_user.user_id}"

        # Step 1: Check if this brand already exists in a project owned by this user
        brand_name_lower = setup_data.brand_name.strip().lower()
        existing_project_query = (
            select(BrandPromptTable.project_id, BrandPromptTable.brand_id)
            .where(
                func.lower(BrandPromptTable.brand_name) == brand_name_lower,
                BrandPromptTable.user_id == current_user.user_id,
                BrandPromptTable.is_active == True
            )
            .limit(1)
        )
        existing_project_result = await db.execute(existing_project_query)
        existing_project_row = existing_project_result.first()

        if existing_project_row:
            # Brand already used in an existing project — find the project name
            project_query = select(ProjectsRecord.project_name).where(
                ProjectsRecord.project_id == existing_project_row.project_id,
                ProjectsRecord.is_active == True
            )
            project_result = await db.execute(project_query)
            existing_project_name = project_result.scalar_one_or_none() or "Unknown"

            logger.info(
                f"Brand '{setup_data.brand_name}' already exists in project "
                f"'{existing_project_name}' for user: {current_user.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Brand \"{setup_data.brand_name.strip()}\" already exists in project \"{existing_project_name}\". Please edit the existing project instead of creating a new one."
            )

        # Step 2: Generate project ID with prefix
        project_id = generate_id("P_")

        # Step 3: Create new brand with B_ prefix
        brand_id = generate_id("B_")
        new_brand = BrandsTable(
            brand_id=brand_id,
            brand_name=setup_data.brand_name.strip(),
            created_by=current_user.user_id
        )
        db.add(new_brand)
        logger.info(f"Creating new brand: {brand_id} for user: {current_user.user_id}")

        # Step 4: Create project
        new_project = ProjectsRecord(
            project_id=project_id,
            project_name=setup_data.project_name.strip(),
            description=setup_data.project_description,
            company_id=company_id,
            created_by=current_user.user_id,
            is_active=True
        )
        db.add(new_project)
        logger.info(f"Creating project: {project_id}")

        # Step 5: Create project-user relationship with OWNER role
        project_user = ProjectUserTable(
            project_id=project_id,
            user_id=current_user.user_id,
            user_role=ProjectRole.OWNER
        )
        db.add(project_user)
        logger.info(f"Creating project-user relationship: {project_id} -> {current_user.user_id} (OWNER)")

        # Step 6: Create brand prompts for each segment (each segment is a separate row)
        prompt_count = 0
        for segment in setup_data.segments:
            if segment.segment_name.strip() and segment.prompts.strip():
                # Generate unique IDs for prompt and idempotency key
                prompt_id = str(uuid.uuid4())
                idempotency_key = str(uuid.uuid4())

                new_prompt = BrandPromptTable(
                    brand_id=brand_id,
                    brand_name=setup_data.brand_name.strip(),
                    prompt=segment.prompts.strip(),
                    prompt_id=prompt_id,
                    segment=segment.segment_name.strip(),
                    project_id=project_id,
                    user_id=current_user.user_id,
                    company_id=company_id,
                    idempotency_key=idempotency_key,
                    is_active=True
                )
                db.add(new_prompt)
                prompt_count += 1
                logger.info(f"Creating prompt for segment: {segment.segment_name}")

        # Commit all changes
        await db.commit()

        logger.info(
            f"Project setup completed: project_id={project_id}, "
            f"brand_id={brand_id}, prompts={prompt_count}"
        )

        return ProjectSetupResponse(
            project_id=project_id,
            brand_id=brand_id,
            prompt_count=prompt_count,
            message="Project setup completed successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions (e.g. 409 Conflict) without wrapping
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to setup project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup project: {str(e)}"
        )


@router.patch("/{project_id}", response_model=ProjectUpdateResponse)
async def update_project(
    project_id: str,
    update_data: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Update an existing project.

    This endpoint allows updating project name, description, and active status.
    Only the owner of the project can update it.

    Args:
        project_id: The project ID to update
        update_data: Fields to update
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectUpdateResponse with success message

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If project not found or user doesn't own it
        HTTPException 500: If update fails
    """
    logger.info(f"Updating project {project_id} for user: {current_user.user_id}")

    try:
        # Find the project and verify ownership
        query = select(ProjectsRecord).where(
            ProjectsRecord.project_id == project_id,
            ProjectsRecord.created_by == current_user.user_id
        )
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            logger.warning(f"Project not found or access denied: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or you don't have permission to update it"
            )

        # Update fields if provided
        if update_data.project_name is not None:
            project.project_name = update_data.project_name.strip()
        if update_data.description is not None:
            project.description = update_data.description.strip() if update_data.description else None
        if update_data.is_active is not None:
            project.is_active = update_data.is_active

        await db.commit()
        await db.refresh(project)

        logger.info(f"Project updated successfully: {project_id}")

        return ProjectUpdateResponse(
            project_id=project_id,
            message="Project updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.put("/{project_id}", response_model=ProjectSetupResponse)
async def update_project_full(
    project_id: str,
    update_data: ProjectFullUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Full update of project including brand and prompts.

    This endpoint performs the following operations:
    1. Updates the project record (name, description, is_active)
    2. Creates or retrieves the brand (case-insensitive match)
    3. Deletes existing prompts for this project
    4. Creates new brand prompt records for each segment

    Args:
        project_id: The project ID to update
        update_data: Full project update data
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectSetupResponse with project ID, brand ID, and prompt count

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If project not found or user doesn't own it
        HTTPException 500: If update fails
    """
    logger.info(
        f"Full update for project {project_id}, user: {current_user.user_id}, "
        f"brand: {update_data.brand_name}"
    )

    try:
        # Find the project and verify ownership
        project_query = select(ProjectsRecord).where(
            ProjectsRecord.project_id == project_id,
            ProjectsRecord.created_by == current_user.user_id
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            logger.warning(f"Project not found or access denied: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or you don't have permission to update it"
            )

        # Get user's company_id from profile
        profile_query = select(UsersProfileTable).where(
            UsersProfileTable.user_id == current_user.user_id
        )
        profile_result = await db.execute(profile_query)
        user_profile = profile_result.scalar_one_or_none()
        company_id = user_profile.company_id if user_profile else f"company_{current_user.user_id}"

        # Step 1: Update project record
        project.project_name = update_data.project_name.strip()
        project.description = update_data.project_description
        project.is_active = update_data.is_active
        logger.info(f"Updating project: {project_id}")

        # Step 2: Check if brand already exists for this user (case-insensitive name + same user)
        brand_name_lower = update_data.brand_name.strip().lower()
        brand_query = select(BrandsTable).where(
            func.lower(BrandsTable.brand_name) == brand_name_lower,
            BrandsTable.created_by == current_user.user_id
        )
        brand_result = await db.execute(brand_query)
        existing_brand = brand_result.scalar_one_or_none()

        if existing_brand:
            brand_id = existing_brand.brand_id
            logger.info(f"Using existing brand: {brand_id} (user already owns this brand)")
        else:
            # Create new brand with B_ prefix
            brand_id = generate_id("B_")
            new_brand = BrandsTable(
                brand_id=brand_id,
                brand_name=update_data.brand_name.strip(),
                created_by=current_user.user_id
            )
            db.add(new_brand)
            logger.info(f"Creating new brand: {brand_id} for user: {current_user.user_id}")

        # Step 3: Delete existing prompts for this project
        delete_stmt = delete(BrandPromptTable).where(
            BrandPromptTable.project_id == project_id
        )
        await db.execute(delete_stmt)
        logger.info(f"Deleted existing prompts for project: {project_id}")

        # Step 4: Create new brand prompts for each segment
        prompt_count = 0
        for segment in update_data.segments:
            if segment.segment_name.strip() and segment.prompts.strip():
                prompt_id = str(uuid.uuid4())
                idempotency_key = str(uuid.uuid4())

                new_prompt = BrandPromptTable(
                    brand_id=brand_id,
                    brand_name=update_data.brand_name.strip(),
                    prompt=segment.prompts.strip(),
                    prompt_id=prompt_id,
                    segment=segment.segment_name.strip(),
                    project_id=project_id,
                    user_id=current_user.user_id,
                    company_id=company_id,
                    idempotency_key=idempotency_key,
                    is_active=True
                )
                db.add(new_prompt)
                prompt_count += 1
                logger.info(f"Creating prompt for segment: {segment.segment_name}")

        # Commit all changes
        await db.commit()

        logger.info(
            f"Project full update completed: project_id={project_id}, "
            f"brand_id={brand_id}, prompts={prompt_count}"
        )

        return ProjectSetupResponse(
            project_id=project_id,
            brand_id=brand_id,
            prompt_count=prompt_count,
            message="Project updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to fully update project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", response_model=ProjectUpdateResponse)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Delete a project and its associated brand prompts.

    This endpoint performs the following operations:
    1. Verifies project ownership
    2. Deletes all brand prompts associated with the project
    3. Deletes the project record

    Args:
        project_id: The project ID to delete
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ProjectUpdateResponse with success message

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If project not found or user doesn't own it
        HTTPException 500: If delete fails
    """
    logger.info(f"Deleting project {project_id} for user: {current_user.user_id}")

    try:
        # Find the project and verify ownership
        project_query = select(ProjectsRecord).where(
            ProjectsRecord.project_id == project_id,
            ProjectsRecord.created_by == current_user.user_id
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            logger.warning(f"Project not found or access denied: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or you don't have permission to delete it"
            )

        # Step 1: Delete all brand prompts for this project
        delete_prompts_stmt = delete(BrandPromptTable).where(
            BrandPromptTable.project_id == project_id
        )
        prompts_result = await db.execute(delete_prompts_stmt)
        deleted_prompts_count = prompts_result.rowcount
        logger.info(f"Deleted {deleted_prompts_count} prompts for project: {project_id}")

        # Step 2: Delete all project-user relationships for this project
        delete_project_users_stmt = delete(ProjectUserTable).where(
            ProjectUserTable.project_id == project_id
        )
        await db.execute(delete_project_users_stmt)
        logger.info(f"Deleted project-user relationships for project: {project_id}")

        # Step 3: Delete the project
        delete_project_stmt = delete(ProjectsRecord).where(
            ProjectsRecord.project_id == project_id
        )
        await db.execute(delete_project_stmt)
        logger.info(f"Deleted project: {project_id}")

        # Commit all changes
        await db.commit()

        logger.info(f"Project deletion completed: {project_id}")

        return ProjectUpdateResponse(
            project_id=project_id,
            message=f"Project deleted successfully (including {deleted_prompts_count} prompts)"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
