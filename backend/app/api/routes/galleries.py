import uuid
from typing import Any

import os
from io import BytesIO
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, StreamingResponse

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    GalleriesPublic,
    GalleryCreate,
    GalleryPublic,
    GalleryUpdate,
    Message,
    PhotosPublic,
    PhotoCreate,
    PhotoPublic,
)

router = APIRouter()


STORAGE_ROOT = Path(os.getenv("GALLERY_STORAGE_ROOT", "app_data/galleries")).resolve()


def _gallery_storage_dir(gallery_id: uuid.UUID) -> Path:
    return STORAGE_ROOT / str(gallery_id)


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
            if (
                not current_user.organization_id
                or project.organization_id != current_user.organization_id
            ):
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
            for pid in project_ids[skip : skip + limit]:
                project_galleries = crud.get_galleries_by_project(
                    session=session, project_id=pid, skip=0, limit=100
                )
                galleries.extend(project_galleries)

            count = sum(
                len(
                    crud.get_galleries_by_project(
                        session=session, project_id=pid, skip=0, limit=1000
                    )
                )
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


@router.get("/{id}/photos", response_model=PhotosPublic)
def list_gallery_photos(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """List photos in a gallery. Visible to clients with access and team in org."""
    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Access check (same as read_gallery)
    user_type = getattr(current_user, "user_type", None)
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if user_type == "client":
        if not crud.user_has_project_access(
            session=session, project_id=project.id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        if (
            not current_user.organization_id
            or project.organization_id != current_user.organization_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

    photos = crud.get_photos_by_gallery(session=session, gallery_id=id, skip=skip, limit=limit)
    return PhotosPublic(
        data=[PhotoPublic.model_validate(p) for p in photos], count=len(photos)
    )


@router.post("/{id}/photos", response_model=PhotosPublic)
async def upload_gallery_photos(
    id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    files: list[UploadFile] = File(...),
) -> Any:
    """Upload one or more photos to a gallery. Only team members; max 20 photos total per gallery."""
    # Permission: only team members
    user_type = getattr(current_user, "user_type", None)
    if user_type != "team_member":
        raise HTTPException(status_code=403, detail="Only team members can upload photos")

    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Org check
    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Enforce max 20 photos
    existing_count = crud.count_photos_in_gallery(session=session, gallery_id=id)
    if existing_count + len(files) > 20:
        raise HTTPException(
            status_code=400, detail="Gallery can hold at most 20 photos"
        )

    storage_dir = _gallery_storage_dir(id)
    storage_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for uf in files:
        # Normalize filename
        safe_name = os.path.basename(uf.filename or "photo")
        target_path = storage_dir / safe_name
        # If duplicate filename, add suffix
        counter = 1
        while target_path.exists():
            stem = Path(safe_name).stem
            ext = Path(safe_name).suffix
            target_path = storage_dir / f"{stem}-{counter}{ext}"
            counter += 1
        content = await uf.read()
        file_size = len(content)  # Get file size in bytes
        with open(target_path, "wb") as out:
            out.write(content)

        # Create photo record; url points to file-serving endpoint
        rel_filename = target_path.name
        photo = crud.create_photo(
            session=session,
            photo_in=PhotoCreate(
                gallery_id=id,
                filename=rel_filename,
                url=f"/api/v1/galleries/{id}/photos/files/{rel_filename}",
                file_size=file_size,
            ),
        )
        saved.append(photo)

    return PhotosPublic(
        data=[PhotoPublic.model_validate(p) for p in saved], count=len(saved)
    )


@router.delete("/{id}/photos")
def delete_gallery_photos(
    id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    photo_ids: list[uuid.UUID] = Body(..., embed=True),
) -> Message:
    """Delete selected photos. Only team members. Also removes files from storage."""
    user_type = getattr(current_user, "user_type", None)
    if user_type != "team_member":
        raise HTTPException(status_code=403, detail="Only team members can delete photos")

    gallery = crud.get_gallery(session=session, gallery_id=id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    project = crud.get_project(session=session, project_id=gallery.project_id)
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Remove files
    storage_dir = _gallery_storage_dir(id)
    deleted = 0
    from sqlmodel import select
    from app.models import Photo

    for pid in photo_ids:
        photo = session.get(Photo, pid)
        if photo and photo.gallery_id == id:
            file_path = storage_dir / photo.filename
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
            deleted += 1

    # Remove db rows
    crud.delete_photos(session=session, gallery_id=id, photo_ids=photo_ids)

    return Message(message=f"Deleted {deleted} photos")


@router.get("/{id}/photos/files/{filename}")
def get_photo_file(id: uuid.UUID, filename: str) -> Any:
    """Serve a stored photo file publicly."""
    file_path = _gallery_storage_dir(id) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.get("/{id}/download-all")
def download_all_photos(id: uuid.UUID, session: SessionDep) -> Any:
    """Download all photos in the gallery as a ZIP, publicly accessible."""
    storage_dir = _gallery_storage_dir(id)
    if not storage_dir.exists():
        raise HTTPException(status_code=404, detail="Gallery not found or empty")

    # Get project name for filename
    gallery = crud.get_gallery(session=session, gallery_id=id)
    project_name = "Project"
    if gallery:
        project = crud.get_project(session=session, project_id=gallery.project_id)
        if project:
            # Sanitize project name for filename
            project_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in project.name)
            project_name = project_name.replace(" ", "_")

    memfile = BytesIO()
    with zipfile.ZipFile(memfile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in storage_dir.glob("*"):
            if path.is_file():
                zf.write(path, arcname=path.name)
    memfile.seek(0)
    filename = f"Mosaic-{project_name}-Photos.zip"
    return StreamingResponse(
        memfile,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.post("/{id}/photos/download")
def download_selected_photos(
    id: uuid.UUID,
    session: SessionDep,
    photo_ids: list[uuid.UUID] = Body(..., embed=True),
) -> Any:
    """Download selected photos in the gallery as a ZIP, publicly accessible."""
    storage_dir = _gallery_storage_dir(id)
    if not storage_dir.exists():
        raise HTTPException(status_code=404, detail="Gallery not found or empty")

    # Get project name for filename
    gallery = crud.get_gallery(session=session, gallery_id=id)
    project_name = "Project"
    if gallery:
        project = crud.get_project(session=session, project_id=gallery.project_id)
        if project:
            # Sanitize project name for filename
            project_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in project.name)
            project_name = project_name.replace(" ", "_")

    # Collect filenames by reading DB
    from app.models import Photo
    files: list[Path] = []
    for pid in photo_ids:
        photo = session.get(Photo, pid)
        # Fallback: construct by filename only if not found
        if photo and photo.gallery_id == id:
            fp = storage_dir / photo.filename
            if fp.exists():
                files.append(fp)

    if not files:
        raise HTTPException(status_code=404, detail="No matching photos found")

    memfile = BytesIO()
    with zipfile.ZipFile(memfile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=path.name)
    memfile.seek(0)
    filename = f"Mosaic-{project_name}-Photos.zip"
    return StreamingResponse(
        memfile,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )

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
        if (
            not current_user.organization_id
            or project.organization_id != current_user.organization_id
        ):
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
