import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    InteractionTypeEnum,
    RacePublic,
    RacesPublic,
    UserProfileCreate,
    UserProfilePublic,
    UserProfileUpdate,
    UserRaceInteractionPublic,
)

router = APIRouter(tags=["profiles"])


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------


@router.get("/users/me/profile", response_model=UserProfilePublic)
def get_my_profile(session: SessionDep, current_user: CurrentUser) -> Any:
    """Return the current user's running profile."""
    profile = crud.get_user_profile(session=session, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return UserProfilePublic.model_validate(profile)


@router.post("/users/me/profile", response_model=UserProfilePublic)
def upsert_my_profile(
    *, session: SessionDep, current_user: CurrentUser, profile_in: UserProfileCreate
) -> Any:
    """Create or replace the current user's running profile."""
    profile = crud.upsert_user_profile(
        session=session, user_id=current_user.id, profile_in=profile_in
    )
    return UserProfilePublic.model_validate(profile)


@router.patch("/users/me/profile", response_model=UserProfilePublic)
def update_my_profile(
    *, session: SessionDep, current_user: CurrentUser, profile_in: UserProfileUpdate
) -> Any:
    """Partially update the current user's running profile."""
    profile = crud.get_user_profile(session=session, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Use POST to create one.")
    profile = crud.update_user_profile(
        session=session, db_profile=profile, profile_in=profile_in
    )
    return UserProfilePublic.model_validate(profile)


@router.delete("/users/me/profile")
def delete_my_profile(session: SessionDep, current_user: CurrentUser) -> Any:
    """Delete the current user's running profile and reset onboarding state."""
    deleted = crud.delete_user_profile(session=session, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}


# ---------------------------------------------------------------------------
# Saved races
# ---------------------------------------------------------------------------


@router.get("/users/me/saved-races", response_model=RacesPublic)
def get_my_saved_races(session: SessionDep, current_user: CurrentUser) -> Any:
    """Return all races the current user has saved."""
    races = crud.get_user_saved_races(session=session, user_id=current_user.id)
    return RacesPublic(
        data=[RacePublic.model_validate(r) for r in races], count=len(races)
    )


@router.post("/races/{race_id}/save", response_model=UserRaceInteractionPublic)
def save_race(
    *, session: SessionDep, current_user: CurrentUser, race_id: uuid.UUID
) -> Any:
    """Save a race to the current user's wishlist."""
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    existing = crud.get_user_interaction(
        session=session,
        user_id=current_user.id,
        race_id=race_id,
        action=InteractionTypeEnum.SAVED,
    )
    if existing:
        return UserRaceInteractionPublic.model_validate(existing)
    interaction = crud.record_interaction(
        session=session,
        user_id=current_user.id,
        race_id=race_id,
        action=InteractionTypeEnum.SAVED,
    )
    return UserRaceInteractionPublic.model_validate(interaction)


@router.delete("/races/{race_id}/save")
def unsave_race(
    *, session: SessionDep, current_user: CurrentUser, race_id: uuid.UUID
) -> Any:
    """Remove a race from the current user's wishlist."""
    existing = crud.get_user_interaction(
        session=session,
        user_id=current_user.id,
        race_id=race_id,
        action=InteractionTypeEnum.SAVED,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Race not in saved list")
    crud.record_interaction(
        session=session,
        user_id=current_user.id,
        race_id=race_id,
        action=InteractionTypeEnum.UNSAVED,
    )
    return {"message": "Race removed from saved list"}


# ---------------------------------------------------------------------------
# Interaction tracking
# ---------------------------------------------------------------------------


@router.post("/races/{race_id}/view", response_model=UserRaceInteractionPublic)
def track_race_view(
    *, session: SessionDep, current_user: CurrentUser, race_id: uuid.UUID
) -> Any:
    """Record that the current user viewed a race detail page."""
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    interaction = crud.record_interaction(
        session=session,
        user_id=current_user.id,
        race_id=race_id,
        action=InteractionTypeEnum.VIEWED,
    )
    return UserRaceInteractionPublic.model_validate(interaction)
