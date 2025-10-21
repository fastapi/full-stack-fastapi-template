import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Gallery,
    GalleryCreate,
    GalleryPublic,
    GalleriesPublic,
    GalleryUpdate,
    Project,
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
    Otherwise, get all galleries for the user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if project_id:
        # Verify project belongs to user's organization
        project = crud.get_project(session=session, project_id=project_id)
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        galleries = crud.get_galleries_by_project(
            session=session, project_id=project_id, skip=skip, limit=limit
        )
        count = len(galleries)  # Simple count for project galleries
    else:
        galleries = crud.get_galleries_by_organization(
            session=session, organization_id=current_user.organization_id, skip=skip, limit=limit
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
    Create new gallery.
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
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
    
    # Check if gallery's project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
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
    Update a gallery.
    """
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    
    # Check if gallery's project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    gallery = crud.update_gallery(session=session, db_gallery=gallery, gallery_in=gallery_in)
    return gallery


@router.delete("/{id}")
def delete_gallery(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a gallery.
    """
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    
    # Check if gallery's project belongs to user's organization
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud.delete_gallery(session=session, gallery_id=id)
    return Message(message="Gallery deleted successfully")

