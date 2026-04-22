import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

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
    RacesPublic,
    RacesPublicWithDistance,
    RaceStatusEnum,
    RaceUpdate,
    TerrainEnum,
)

router = APIRouter(prefix="/races", tags=["races"])


# ---------------------------------------------------------------------------
# Discovery / search endpoints  (must come before /{race_id})
# ---------------------------------------------------------------------------


@router.get("/search", response_model=RacesPublic)
def search_races(
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
    sort: str = Query(default="date", pattern="^(date|distance|popularity)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Any:
    """Search races with full-text, geo radius, distance, terrain, and tag filters."""
    races = crud.search_races(
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
        sort=sort,
        skip=skip,
        limit=limit,
    )
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
def get_trending_races(
    session: SessionDep,
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=10, ge=1, le=50),
) -> Any:
    """Return trending races based on interaction count over the last N days."""
    races = crud.get_trending_races(session=session, days=days, limit=limit)
    return RacesPublic(
        data=[RacePublic.model_validate(r) for r in races], count=len(races)
    )


@router.get("/recommended", response_model=RacesPublic)
def get_recommended_races(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(default=10, ge=1, le=50),
) -> Any:
    """Return personalized race recommendations based on user profile."""
    races = crud.get_recommended_races(
        session=session, user_id=current_user.id, limit=limit
    )
    return RacesPublic(
        data=[RacePublic.model_validate(r) for r in races], count=len(races)
    )


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


@router.post("/", response_model=RacePublic)
def create_race(
    *, session: SessionDep, current_user: CurrentUser, race_in: RaceCreate
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
    return race


@router.delete("/{race_id}", response_model=Message)
def delete_race(
    *, session: SessionDep, current_user: CurrentUser, race_id: uuid.UUID
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
    return Message(message="Race deleted successfully")
