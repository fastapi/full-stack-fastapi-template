import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import RaceTagCreate, TagPublic, TagsPublic, TagTranslationUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsPublic)
async def list_tags(session: SessionDep) -> Any:
    """List all available race tags. Public endpoint. Cached 10 minutes."""
    from app.services.cache import cache_get, cache_set

    cache_key = "tags:all"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    tags = crud.get_all_tags(session=session)
    count = crud.get_all_tags_count(session=session)
    result = TagsPublic(data=[TagPublic.model_validate(t) for t in tags], count=count)
    await cache_set(cache_key, result.model_dump(), ttl=600)  # 10 min TTL
    return result


@router.post("/", response_model=TagPublic)
def create_tag(
    *, session: SessionDep, current_user: CurrentUser, tag_in: RaceTagCreate
) -> Any:
    """Create a new tag. Admin only."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    existing = crud.get_tag_by_slug(session=session, slug=tag_in.slug)
    if existing:
        raise HTTPException(status_code=409, detail="Tag with this slug already exists")
    tag = crud.get_or_create_tag(session=session, tag_in=tag_in)
    return TagPublic.model_validate(tag)


@router.post("/{race_id}/tags", response_model=list[TagPublic])
def set_tags_for_race(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    race_id: uuid.UUID,
    tag_ids: list[uuid.UUID],
) -> Any:
    """Replace the full tag list on a race. Organizer or admin only."""
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    race = crud.set_race_tags(session=session, race=race, tag_ids=tag_ids)
    return [TagPublic.model_validate(t) for t in race.tags]


@router.put("/{tag_id}/translations", response_model=TagPublic)
def update_tag_translations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    tag_id: uuid.UUID,
    translation: TagTranslationUpdate,
) -> Any:
    """
    Update translations for a tag.
    Admin only.
    """
    from app.i18n import is_language_supported, set_translation
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the tag
    tag = crud.get_tag(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Validate language
    if not is_language_supported(translation.language):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{translation.language}' is not supported"
        )
    
    # Update translations
    if translation.name:
        set_translation(tag, "name", translation.name, translation.language)
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return TagPublic.model_validate(tag)


@router.get("/{tag_id}/translations", response_model=dict[str, Any])
def get_tag_translations(
    *,
    session: SessionDep,
    tag_id: uuid.UUID,
) -> Any:
    """
    Get all translations for a tag.
    Public endpoint - anyone can view translations.
    """
    tag = crud.get_tag(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return tag.translations or {}

