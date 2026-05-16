import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from sqlmodel import SQLModel
from app.api.rate_limit import RateLimiter

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    DifficultyEnum,
    Message,
    RaceCategoryPublic,
    RaceCreate,
    RacePublic,
    RacePublicWithDetails,
    RacePublicWithDistance,
    RacePublicWithExplanation,
    RacesPublic,
    RacesPublicWithDistance,
    RacesPublicWithExplanation,
    RaceStatusEnum,
    RaceUpdate,
    TerrainEnum,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/races", tags=["races"])


def _invalidate_race_caches() -> None:
    """Synchronously schedule cache invalidation for race-related keys."""
    import asyncio
    from app.services.cache import cache_delete_pattern

    async def _run() -> None:
        await cache_delete_pattern("trending:*")
        await cache_delete_pattern("search:*")
        await cache_delete_pattern("tags:*")

    asyncio.create_task(_run())


def _schedule_embedding(race_id: uuid.UUID) -> None:
    """Fire-and-forget: compute and persist the race embedding asynchronously."""
    from app.core.db import engine
    from app.services.ai import embed_race
    from sqlmodel import Session

    async def _run() -> None:
        try:
            with Session(engine) as session:
                race = crud.get_race(session=session, race_id=race_id)
                if race is None:
                    return
                vector = await embed_race(race)
                crud.update_race_embedding(
                    session=session, race_id=race_id, embedding=vector
                )
        except Exception:
            logger.exception("Failed to embed race %s", race_id)

    asyncio.create_task(_run())


# ---------------------------------------------------------------------------
# Discovery / search endpoints  (must come before /{race_id})
# ---------------------------------------------------------------------------


@router.get("/search", response_model=RacesPublic)
async def search_races(
    session: SessionDep,
    q: str | None = Query(default=None, description="Full-text search query"),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lon: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float | None = Query(default=None, gt=0),
    distance_min_km: float | None = Query(default=None, gt=0),
    distance_max_km: float | None = Query(default=None, gt=0),
    terrain: TerrainEnum | None = None,
    difficulty: DifficultyEnum | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    tag_slugs: list[str] | None = Query(default=None),
    status: RaceStatusEnum | None = None,
    province_code: str | None = Query(default=None, description="Filter by province code"),
    ward_code: str | None = Query(default=None, description="Filter by ward code"),
    sort: str = Query(default="date", pattern="^(date|distance|popularity)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Any:
    """Search races with full-text + semantic vector search (RRF fusion), geo, and filters."""
    from app.services.ai import embed_text
    from app.core.config import settings

    # When a text query is provided and embeddings are configured, run semantic search
    # in parallel with FTS and merge via Reciprocal Rank Fusion.
    vec_ids: list[tuple[uuid.UUID, int]] = []
    if q and settings.OPENAI_API_KEY:
        try:
            query_embedding = await embed_text(q)
            vec_ids = crud.semantic_search_races(
                session=session, query_embedding=query_embedding, limit=limit * 2
            )
        except Exception:
            logger.warning("Semantic search failed; falling back to FTS only")

    # FTS + filter query
    fts_races = crud.search_races(
        session=session,
        q=q,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        distance_min_km=distance_min_km,
        distance_max_km=distance_max_km,
        terrain=terrain,
        difficulty=difficulty,
        date_from=date_from,
        date_to=date_to,
        tag_slugs=tag_slugs,
        status=status,
        province_code=province_code,
        ward_code=ward_code,
        sort=sort,
        skip=0,
        limit=limit * 2,
    )

    if q and vec_ids:
        # RRF fusion: merge semantic and FTS ranked lists
        fts_ids = [r.id for r in fts_races]
        merged_ids = crud.rrf_merge_race_ids(fts_ids, vec_ids, limit=limit + skip)
        merged_ids_page = merged_ids[skip : skip + limit]

        # Preserve order from merge result
        id_to_race = {r.id: r for r in fts_races}
        # Fetch any vector results not in FTS results
        remaining = [rid for rid in merged_ids_page if rid not in id_to_race]
        if remaining:
            extra = crud.get_races_by_ids(session=session, race_ids=remaining)
            id_to_race.update({r.id: r for r in extra})

        races = [id_to_race[rid] for rid in merged_ids_page if rid in id_to_race]
        count = len(merged_ids)
    else:
        races = fts_races[skip : skip + limit]
        count = crud.search_races_count(
            session=session,
            q=q,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            distance_min_km=distance_min_km,
            distance_max_km=distance_max_km,
            terrain=terrain,
            difficulty=difficulty,
            date_from=date_from,
            date_to=date_to,
            tag_slugs=tag_slugs,
            status=status,
            province_code=province_code,
            ward_code=ward_code,
        )

    return RacesPublic(data=[RacePublic.model_validate(r) for r in races], count=count)


@router.get("/nearby", response_model=RacesPublicWithDistance)
def get_nearby_races(
    session: SessionDep,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=100.0, gt=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Any:
    """Return races within radius_km of the given coordinates, sorted by distance."""
    pairs = crud.get_nearby_races(
        session=session, lat=lat, lon=lon, radius_km=radius_km, limit=limit
    )
    data = [
        RacePublicWithDistance(**race.model_dump(), distance_km=dist_km)
        for race, dist_km in pairs
    ]
    return RacesPublicWithDistance(data=data, count=len(data))


@router.get("/trending", response_model=RacesPublic)
async def get_trending_races(
    session: SessionDep,
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=10, ge=1, le=50),
) -> Any:
    """Return trending races based on interaction count over the last N days."""
    from app.services.cache import cache_get, cache_set

    cache_key = f"trending:{days}:{limit}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    races = crud.get_trending_races(session=session, days=days, limit=limit)
    result = RacesPublic(
        data=[RacePublic.model_validate(r) for r in races], count=len(races)
    )
    await cache_set(cache_key, result.model_dump(), ttl=300)  # 5 min TTL
    return result


@router.get(
    "/recommended",
    response_model=RacesPublicWithExplanation,
    dependencies=[RateLimiter(max_calls=30, window_seconds=60)],
)
async def get_recommended_races(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(default=10, ge=1, le=50),
) -> Any:
    """Return personalized race recommendations with AI-generated explanations."""
    from app.services.ai import generate_race_recommendation_explanation
    from app.core.config import settings

    races = crud.get_recommended_races(
        session=session, user_id=current_user.id, limit=limit
    )
    profile = crud.get_user_profile(session=session, user_id=current_user.id)

    results: list[RacePublicWithExplanation] = []
    for race in races:
        explanation: str | None = None
        if settings.ANTHROPIC_API_KEY:
            try:
                explanation = await generate_race_recommendation_explanation(
                    race=race, profile=profile
                )
            except Exception:
                logger.warning("Failed to generate explanation for race %s", race.id)
        results.append(
            RacePublicWithExplanation(**race.model_dump(), ai_explanation=explanation)
        )

    return RacesPublicWithExplanation(data=results, count=len(results))


@router.get("/my/organized", response_model=RacesPublic)
def read_my_organized_races(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve races organized by the current user.
    Requires organizer or admin role.
    """
    if not current_user.is_superuser and not crud.user_has_any_role(
        current_user, ["organizer", "admin"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Only organizers and admins can access this endpoint",
        )

    races = crud.get_races(
        session=session, skip=skip, limit=limit, organizer_id=current_user.id
    )
    count = crud.get_races_count(session=session, organizer_id=current_user.id)
    races_public = [RacePublic.model_validate(race) for race in races]
    return RacesPublic(data=races_public, count=count)


# ---------------------------------------------------------------------------
# Collection + item endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=RacesPublic)
def read_races(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    organizer_id: uuid.UUID | None = None,
) -> Any:
    """
    Retrieve races. Public endpoint - anyone can view races.
    Optionally filter by organizer_id.
    """
    races = crud.get_races(
        session=session, skip=skip, limit=limit, organizer_id=organizer_id
    )
    count = crud.get_races_count(session=session, organizer_id=organizer_id)
    races_public = [RacePublic.model_validate(race) for race in races]
    return RacesPublic(data=races_public, count=count)


# AI Assistant endpoint
class RaceNameInput(SQLModel):
    name: str


class AIRaceSuggestion(SQLModel):
    description: str | None = None
    location: str | None = None
    terrain_type: str | None = None
    difficulty_level: str | None = None
    elevation_gain_m: str | None = None


@router.post("/ai-assist", response_model=AIRaceSuggestion)
async def generate_race_details(
    *,
    current_user: CurrentUser,
    race_name_input: RaceNameInput,
) -> Any:
    """
    Use AI to generate race details from a race name.
    Requires authentication.
    """
    from app.services.ai import generate_race_from_name
    from app.core.config import settings

    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI assistance is not configured. Please set OPENAI_API_KEY.",
        )

    details = await generate_race_from_name(race_name_input.name)
    return AIRaceSuggestion(**details)


@router.post("/", response_model=RacePublic)
def create_race(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    race_in: RaceCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create new race.
    Requires organizer or admin role.
    """
    if not current_user.is_superuser and not crud.user_has_any_role(
        current_user, ["organizer", "admin"]
    ):
        raise HTTPException(
            status_code=403, detail="Only organizers and admins can create races"
        )

    race = crud.create_race(
        session=session, race_in=race_in, organizer_id=current_user.id
    )
    background_tasks.add_task(_schedule_embedding, race.id)
    background_tasks.add_task(_invalidate_race_caches)
    return race


@router.get("/{race_id}", response_model=RacePublicWithDetails)
def read_race(session: SessionDep, race_id: uuid.UUID) -> Any:
    """
    Get race by ID with details. Public endpoint.
    """
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    categories = crud.get_race_categories(session=session, race_id=race_id)
    categories_public = [RaceCategoryPublic.model_validate(cat) for cat in categories]
    registration_count = crud.get_race_registrations_count(
        session=session, race_id=race_id
    )
    tags = crud.get_race_tags(session=session, race_id=race_id)

    return RacePublicWithDetails(
        **race.model_dump(),
        categories=categories_public,
        registration_count=registration_count,
        tags=tags,
    )


@router.get("/{race_id}/similar", response_model=RacesPublic)
def get_similar_races(
    session: SessionDep,
    race_id: uuid.UUID,
    limit: int = Query(default=6, ge=1, le=20),
) -> Any:
    """Return races similar to the given race."""
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    races = crud.get_similar_races(session=session, race=race, limit=limit)
    return RacesPublic(
        data=[RacePublic.model_validate(r) for r in races], count=len(races)
    )


@router.put("/{race_id}", response_model=RacePublic)
def update_race(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    race_id: uuid.UUID,
    race_in: RaceUpdate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Update a race.
    Only the organizer or admin can update.
    """
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    race = crud.update_race(session=session, db_race=race, race_in=race_in)
    background_tasks.add_task(_schedule_embedding, race.id)
    background_tasks.add_task(_invalidate_race_caches)
    return race


@router.delete("/{race_id}", response_model=Message)
def delete_race(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    race_id: uuid.UUID,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Delete a race.
    Only the organizer or admin can delete.
    """
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race(session=session, race_id=race_id)
    background_tasks.add_task(_invalidate_race_caches)
    return Message(message="Race deleted successfully")


# ---------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------


class TagSuggestion(SQLModel):
    tags: list[str]


class DescriptionSuggestion(SQLModel):
    description: str


class RaceAnswer(SQLModel):
    answer: str


class AskRequest(SQLModel):
    question: str


@router.post("/{race_id}/auto-tag", response_model=TagSuggestion)
async def auto_tag_race(session: SessionDep, race_id: uuid.UUID) -> Any:
    """Suggest tags for a race using AI (does not save — returns suggestions only)."""
    from app.services.ai import suggest_race_tags

    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    tags = await suggest_race_tags(race)
    return TagSuggestion(tags=tags)


@router.post(
    "/{race_id}/enhance-description",
    response_model=DescriptionSuggestion,
    dependencies=[RateLimiter(max_calls=5, window_seconds=60)],
)
async def enhance_race_description(session: SessionDep, race_id: uuid.UUID) -> Any:
    """Suggest an improved description using AI (does not save — returns suggestion only)."""
    from app.services.ai import enhance_race_description as _enhance

    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    description = await _enhance(race)
    return DescriptionSuggestion(description=description)



@router.post(
    "/{race_id}/ask",
    response_model=RaceAnswer,
    dependencies=[RateLimiter(max_calls=10, window_seconds=60)],
)
async def ask_race_question(
    session: SessionDep,
    race_id: uuid.UUID,
    body: AskRequest,
) -> Any:
    """Answer a question about a specific race using AI. Rate limited to 10 req/min per IP."""
    from app.services.ai import answer_race_question

    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    answer = await answer_race_question(race=race, question=body.question)
    return RaceAnswer(answer=answer)


# ---------------------------------------------------------------------------
# Admin utilities
# ---------------------------------------------------------------------------

admin_router = APIRouter(prefix="/admin/races", tags=["admin"])


@admin_router.post("/reindex", response_model=Message)
def reindex_race_embeddings(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    batch_size: int = Query(default=50, ge=1, le=200),
) -> Any:
    """
    Queue embedding generation for all races that lack an embedding.
    Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    races_to_index = crud.get_races_without_embedding(
        session=session, limit=batch_size
    )
    for race in races_to_index:
        background_tasks.add_task(_schedule_embedding, race.id)

    return Message(
        message=f"Queued {len(races_to_index)} race(s) for embedding generation"
    )
