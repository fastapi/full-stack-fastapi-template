import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    GalleriesPublic,
    GalleryCreate,
    GalleryPublic,
    GalleryUpdate,
    Message,
)

router = APIRouter()


@router.get("/", response_model=GalleriesPublic)
def read_galleries(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve galleries. If project_id is provided, get galleries for that project.
    Otherwise, get all galleries based on user type:
    - Team members: all galleries from their organization
    - Clients: galleries from projects they have access to
    """
    user_type = getattr(current_user, "user_type", None)

    if project_id:
        # Verify user has access to this project
        project = crud.get_project(session=session, project_id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check access based on user type
        if user_type == "client":
            # Client must have explicit access
            if not crud.user_has_project_access(
                session=session, project_id=project_id, user_id=current_user.id
            ):
                raise HTTPException(status_code=403, detail="Not enough permissions")
        else:
            # Team member must be in same organization
            if not current_user.organization_id or project.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

        galleries = crud.get_galleries_by_project(
            session=session, project_id=project_id, skip=skip, limit=limit
        )
        count = len(galleries)  # Simple count for project galleries
    else:
        # No specific project - list all accessible galleries
        if user_type == "client":
            # Get galleries from all projects the client has access to
            accessible_projects = crud.get_user_accessible_projects(
                session=session, user_id=current_user.id, skip=0, limit=1000
            )
            project_ids = [p.id for p in accessible_projects]
            
            # Get galleries for all accessible projects
            galleries = []
            for pid in project_ids[skip:skip+limit]:
                project_galleries = crud.get_galleries_by_project(
                    session=session, project_id=pid, skip=0, limit=100
                )
                galleries.extend(project_galleries)
            
            count = sum(
                len(crud.get_galleries_by_project(session=session, project_id=pid, skip=0, limit=1000))
                for pid in project_ids
            )
        else:
            # Team member - get all galleries from organization
            if not current_user.organization_id:
                raise HTTPException(
                    status_code=400, detail="User is not part of an organization"
                )
            
            galleries = crud.get_galleries_by_organization(
                session=session,
                organization_id=current_user.organization_id,
                skip=skip,
                limit=limit,
            )
            count = crud.count_galleries_by_organization(
                session=session, organization_id=current_user.organization_id
            )

    return GalleriesPublic(data=galleries, count=count)


@router.post("/", response_model=GalleryPublic)
def create_gallery(
    *, session: SessionDep, current_user: CurrentUser, gallery_in: GalleryCreate
) -> Any:
    """
    Create new gallery. Only team members can create galleries.
    """
    user_type = getattr(current_user, "user_type", None)
    
    # Only team members can create galleries
    if user_type != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can create galleries"
        )
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not part of an organization"
        )

    # Verify project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery_in.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gallery = crud.create_gallery(session=session, gallery_in=gallery_in)
    return gallery


@router.get("/{id}", response_model=GalleryPublic)
def read_gallery(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get gallery by ID.
    """
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Check access based on user type
    user_type = getattr(current_user, "user_type", None)
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user_type == "client":
        # Client must have access to the project
        if not crud.user_has_project_access(
            session=session, project_id=project.id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        # Team member must be in same organization
        if not current_user.organization_id or project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return gallery


@router.put("/{id}", response_model=GalleryPublic)
def update_gallery(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    gallery_in: GalleryUpdate,
) -> Any:
    """
    Update a gallery. Only team members can update galleries.
    """
    user_type = getattr(current_user, "user_type", None)
    
    # Only team members can update galleries
    if user_type != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can update galleries"
        )
    
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Check if gallery's project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    gallery = crud.update_gallery(
        session=session, db_gallery=gallery, gallery_in=gallery_in
    )
    return gallery


@router.delete("/{id}")
def delete_gallery(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a gallery. Only team members can delete galleries.
    """
    user_type = getattr(current_user, "user_type", None)
    
    # Only team members can delete galleries
    if user_type != "team_member":
        raise HTTPException(
            status_code=403, detail="Only team members can delete galleries"
        )
    
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Check if gallery's project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_gallery(session=session, gallery_id=id)
    return Message(message="Gallery deleted successfully")
