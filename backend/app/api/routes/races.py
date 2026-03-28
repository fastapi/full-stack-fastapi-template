import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    RaceCategoryPublic,
    RaceCreate,
    RacePublic,
    RacePublicWithDetails,
    RacesPublic,
    RaceUpdate,
)

router = APIRouter(prefix="/races", tags=["races"])


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


@router.get("/{race_id}", response_model=RacePublicWithDetails)
def read_race(session: SessionDep, race_id: uuid.UUID) -> Any:
    """
    Get race by ID with details. Public endpoint.
    """
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Get categories
    categories = crud.get_race_categories(session=session, race_id=race_id)
    categories_public = [RaceCategoryPublic.model_validate(cat) for cat in categories]

    # Get registration count
    registration_count = crud.get_race_registrations_count(
        session=session, race_id=race_id
    )

    return RacePublicWithDetails(
        **race.model_dump(),
        categories=categories_public,
        registration_count=registration_count,
    )


@router.get("/my/organized", response_model=RacesPublic)
def read_my_organized_races(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve races organized by the current user.
    Requires organizer or admin role.
    """
    # Check if user has organizer or admin role
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


@router.post("/", response_model=RacePublic)
def create_race(
    *, session: SessionDep, current_user: CurrentUser, race_in: RaceCreate
) -> Any:
    """
    Create new race.
    Requires organizer or admin role.
    """
    # Check if user has organizer or admin role
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

    # Check permissions
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

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race(session=session, race_id=race_id)
    return Message(message="Race deleted successfully")
