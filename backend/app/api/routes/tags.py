import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import RaceTagCreate, TagPublic, TagsPublic

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsPublic)
def list_tags(session: SessionDep) -> Any:
    """List all available race tags. Public endpoint."""
    tags = crud.get_all_tags(session=session)
    count = crud.get_all_tags_count(session=session)
    return TagsPublic(data=[TagPublic.model_validate(t) for t in tags], count=count)


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
