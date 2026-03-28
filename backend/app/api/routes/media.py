import uuid
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import (
    MediaAssetCreate,
    MediaAssetPublic,
    MediaAssetsPublic,
    MediaAssetUpdate,
    Message,
)
from app.services.media_storage import (
    delete_media_file,
    resolve_media_path,
    save_uploaded_media,
)

router = APIRouter(prefix="/media", tags=["media"])

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
}


def _can_manage_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: str,
    content_id: uuid.UUID,
) -> bool:
    if current_user.is_superuser:
        return True

    if content_type == "race":
        race = crud.get_race(session=session, race_id=content_id)
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")
        return race.organizer_id == current_user.id

    return False


@router.get("/", response_model=MediaAssetsPublic)
def read_media_assets(
    session: SessionDep,
    content_type: str | None = None,
    content_id: uuid.UUID | None = None,
    kind: str | None = None,
    is_public: bool = True,
    skip: int = 0,
    limit: int = 200,
) -> Any:
    """List media assets for any content type."""
    assets = crud.get_media_assets(
        session=session,
        content_type=content_type,
        content_id=content_id,
        kind=kind,
        is_public=is_public,
        skip=skip,
        limit=limit,
    )
    count = crud.get_media_assets_count(
        session=session,
        content_type=content_type,
        content_id=content_id,
        kind=kind,
        is_public=is_public,
    )
    assets_public = [MediaAssetPublic.model_validate(asset) for asset in assets]
    return MediaAssetsPublic(data=assets_public, count=count)


@router.post("/upload", response_model=MediaAssetPublic)
def upload_media_asset(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    content_type: str = Form(...),
    content_id: uuid.UUID = Form(...),
    kind: str = Form("gallery"),
    alt_text: str | None = Form(None),
    display_order: int = Form(0),
    is_primary: bool = Form(False),
    is_public: bool = Form(True),
) -> Any:
    """Upload media for any content type (currently race-aware for permissions)."""
    normalized_content_type = content_type.strip().lower()

    can_manage = _can_manage_content(
        session=session,
        current_user=current_user,
        content_type=normalized_content_type,
        content_id=content_id,
    )
    if not can_manage:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if not file.content_type or file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    stored_filename, relative_path, size_bytes = save_uploaded_media(
        file=file,
        content_type=normalized_content_type,
        content_id=content_id,
    )

    max_size_bytes = settings.MEDIA_MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_size_bytes:
        delete_media_file(relative_path)
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds max size of {settings.MEDIA_MAX_FILE_SIZE_MB}MB",
        )

    if is_primary:
        crud.clear_primary_media(
            session=session,
            content_type=normalized_content_type,
            content_id=content_id,
            kind=kind,
        )

    media_in = MediaAssetCreate(
        content_type=normalized_content_type,
        content_id=content_id,
        kind=kind,
        alt_text=alt_text,
        display_order=display_order,
        is_primary=is_primary,
        is_public=is_public,
        original_filename=file.filename or stored_filename,
        file_name=stored_filename,
        file_path=relative_path,
        file_url="",
        mime_type=file.content_type,
        size_bytes=size_bytes,
        uploaded_by_id=current_user.id,
    )

    db_media = crud.create_media_asset(session=session, media_in=media_in)
    db_media.file_url = f"{settings.API_V1_STR}/media/{db_media.id}/file"
    session.add(db_media)
    session.commit()
    session.refresh(db_media)

    return db_media


@router.get("/{media_id}/file")
def read_media_file(session: SessionDep, media_id: uuid.UUID) -> Any:
    """Serve a media file by media id."""
    media = crud.get_media_asset(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    file_path = resolve_media_path(media.file_path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type=media.mime_type,
        filename=media.original_filename,
    )


@router.put("/{media_id}", response_model=MediaAssetPublic)
def update_media_asset(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: uuid.UUID,
    media_in: MediaAssetUpdate,
) -> Any:
    """Update media metadata."""
    media = crud.get_media_asset(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    can_manage = _can_manage_content(
        session=session,
        current_user=current_user,
        content_type=media.content_type,
        content_id=media.content_id,
    )
    if not can_manage:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    incoming = media_in.model_dump(exclude_unset=True)
    next_kind = incoming.get("kind", media.kind)
    next_is_primary = incoming.get("is_primary", media.is_primary)

    if next_is_primary:
        crud.clear_primary_media(
            session=session,
            content_type=media.content_type,
            content_id=media.content_id,
            kind=next_kind,
            exclude_id=media.id,
        )

    updated = crud.update_media_asset(
        session=session,
        db_media=media,
        media_in=media_in,
    )
    return updated


@router.delete("/{media_id}", response_model=Message)
def delete_media_asset(
    *, session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Any:
    """Delete a media asset and its file."""
    media = crud.get_media_asset(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    can_manage = _can_manage_content(
        session=session,
        current_user=current_user,
        content_type=media.content_type,
        content_id=media.content_id,
    )
    if not can_manage:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_media_file(media.file_path)
    crud.delete_media_asset(session=session, media_id=media_id)
    return Message(message="Media deleted successfully")
