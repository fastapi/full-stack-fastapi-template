import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Project,
    ProjectCreate,
    ProjectPublic,
    ProjectsPublic,
    ProjectUpdate,
    DashboardStats,
)

router = APIRouter()


@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve projects for the current user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    projects = crud.get_projects_by_organization(
        session=session, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    count = crud.count_projects_by_organization(
        session=session, organization_id=current_user.organization_id
    )
    
    return ProjectsPublic(data=projects, count=count)


@router.get("/stats", response_model=DashboardStats)
def read_dashboard_stats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get dashboard statistics for the current user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    return crud.get_dashboard_stats(session=session, organization_id=current_user.organization_id)


@router.post("/", response_model=ProjectPublic)
def create_project(
    *, session: SessionDep, current_user: CurrentUser, project_in: ProjectCreate
) -> Any:
    """
    Create new project.
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    # Ensure the project is being created for the user's organization
    if project_in.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    project = crud.create_project(session=session, project_in=project_in)
    return project


@router.get("/{id}", response_model=ProjectPublic)
def read_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get project by ID.
    """
    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project belongs to user's organization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return project


@router.put("/{id}", response_model=ProjectPublic)
def update_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    project_in: ProjectUpdate,
) -> Any:
    """
    Update a project.
    """
    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project belongs to user's organization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    project = crud.update_project(session=session, db_project=project, project_in=project_in)
    return project


@router.delete("/{id}")
def delete_project(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a project.
    """
    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project belongs to user's organization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud.delete_project(session=session, project_id=id)
    return Message(message="Project deleted successfully")

