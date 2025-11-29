import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    DashboardStats,
    GalleryCreate,
    Message,
    ProjectCreate,
    ProjectPublic,
    ProjectsPublic,
    ProjectUpdate,
)

router = APIRouter()


def _gallery_storage_root() -> Path:
    """Return the root directory where gallery photos are stored.

    Mirrors the logic in app.api.routes.galleries.STORAGE_ROOT without importing it
    directly here to avoid any circular import issues at app startup.
    """
    return Path(os.getenv("GALLERY_STORAGE_ROOT", "app_data/galleries")).resolve()


@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve projects.
    - Team members see projects from their organization
    - Clients see projects they have been invited to
    """
    if getattr(current_user, "user_type", None) == "client":
        # Clients see only projects they have access to
        projects = crud.get_user_accessible_projects(
            session=session,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        count = crud.count_user_accessible_projects(
            session=session, user_id=current_user.id
        )
    else:
        # Team members see projects from their organization
        if not current_user.organization_id:
            raise HTTPException(
                status_code=400, detail="User is not part of an organization"
            )

        projects = crud.get_projects_by_organization(
            session=session,
            organization_id=current_user.organization_id,
            skip=skip,
            limit=limit,
        )
        count = crud.count_projects_by_organization(
            session=session, organization_id=current_user.organization_id
        )

    return ProjectsPublic(data=projects, count=count)


@router.get("/stats", response_model=DashboardStats)
def read_dashboard_stats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get dashboard statistics for the current user's organization.
    Only available to team members.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403, detail="Dashboard stats only available to team members"
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not part of an organization"
        )

    return crud.get_dashboard_stats(
        session=session, organization_id=current_user.organization_id
    )


@router.post("/", response_model=ProjectPublic)
def create_project(
    *, session: SessionDep, current_user: CurrentUser, project_in: ProjectCreate
) -> Any:
    """
    Create new project.
    Only team members can create projects.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can create projects"
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not part of an organization"
        )

    # Ensure the project is being created for the user's organization
    if project_in.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    project = crud.create_project(session=session, project_in=project_in)

    # Automatically create a gallery for the project
    gallery_in = GalleryCreate(
        name=f"{project.name} - Gallery",
        project_id=project.id,
        status="draft",
    )
    crud.create_gallery(session=session, gallery_in=gallery_in)

    return project


@router.get("/{id}", response_model=ProjectPublic)
def read_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get project by ID.
    """
    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permissions based on user type
    if getattr(current_user, "user_type", None) == "client":
        # Clients need explicit access
        if not crud.user_has_project_access(
            session=session, project_id=id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        # Team members need organization match
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
    Only team members from the project's organization can update projects.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can update projects"
        )

    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if project belongs to user's organization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    project = crud.update_project(
        session=session, db_project=project, project_in=project_in
    )
    return project


@router.delete("/{id}")
def delete_project(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a project.
    Only team members from the project's organization can delete projects.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can delete projects"
        )

    project = crud.get_project(session=session, project_id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if project belongs to user's organization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Before deleting the project from DB, remove gallery folders & photos from storage.
    from app.models import Gallery

    storage_root = _gallery_storage_root()

    # Find all galleries for this project
    statement = select(Gallery).where(Gallery.project_id == id)
    galleries = session.exec(statement).all()

    for gallery in galleries:
        gallery_dir = storage_root / str(gallery.id)
        if gallery_dir.exists() and gallery_dir.is_dir():
            # Best-effort recursive delete of all files and subdirs
            for root, dirs, files in os.walk(gallery_dir, topdown=False):
                for name in files:
                    try:
                        (Path(root) / name).unlink()
                    except OSError:
                        pass
                for name in dirs:
                    try:
                        (Path(root) / name).rmdir()
                    except OSError:
                        pass
            try:
                gallery_dir.rmdir()
            except OSError:
                # If something remains locked, ignore; DB rows will still be removed
                pass

    # Delete the project. DB-level cascading will remove galleries & photos.
    crud.delete_project(session=session, project_id=id)
    return Message(message="Project deleted successfully")
