import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    RaceResultCreate,
    RaceResultPublic,
    RaceResultsPublic,
    RaceResultUpdate,
)

router = APIRouter(prefix="/race-results", tags=["race-results"])


@router.get("/", response_model=RaceResultsPublic)
def read_race_results(
    session: SessionDep,
    race_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve race results for a specific race. Public endpoint.
    """
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    results = crud.get_race_results(
        session=session, race_id=race_id, skip=skip, limit=limit
    )
    results_public = [RaceResultPublic.model_validate(result) for result in results]
    return RaceResultsPublic(data=results_public, count=len(results_public))


@router.get("/{result_id}", response_model=RaceResultPublic)
def read_race_result(session: SessionDep, result_id: uuid.UUID) -> Any:
    """
    Get race result by ID. Public endpoint.
    """
    result = crud.get_race_result(session=session, result_id=result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Race result not found")
    return result


@router.get("/registration/{registration_id}", response_model=RaceResultPublic)
def read_race_result_by_registration(
    session: SessionDep, registration_id: uuid.UUID
) -> Any:
    """
    Get race result by registration ID. Public endpoint.
    """
    result = crud.get_race_result_by_registration(
        session=session, registration_id=registration_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Race result not found")
    return result


@router.post("/", response_model=RaceResultPublic)
def create_race_result(
    *, session: SessionDep, current_user: CurrentUser, result_in: RaceResultCreate
) -> Any:
    """
    Create new race result.
    Only race organizers, volunteers, or admins can create results.
    """
    # Get registration to verify race
    registration = crud.get_race_registration(
        session=session, registration_id=result_in.registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions - only organizer, volunteer, or admin
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        if not crud.user_has_any_role(current_user, ["volunteer"]):
            raise HTTPException(
                status_code=403,
                detail="Only race organizers, volunteers, or admins can create results",
            )

    # Check if result already exists
    existing_result = crud.get_race_result_by_registration(
        session=session, registration_id=result_in.registration_id
    )
    if existing_result:
        raise HTTPException(
            status_code=400, detail="Result already exists for this registration"
        )

    result = crud.create_race_result(session=session, result_in=result_in)
    return result


@router.put("/{result_id}", response_model=RaceResultPublic)
def update_race_result(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    result_id: uuid.UUID,
    result_in: RaceResultUpdate,
) -> Any:
    """
    Update a race result.
    Only race organizers, volunteers, or admins can update results.
    """
    result = crud.get_race_result(session=session, result_id=result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Race result not found")

    # Get registration to verify race
    registration = crud.get_race_registration(
        session=session, registration_id=result.registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions - only organizer, volunteer, or admin
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        if not crud.user_has_any_role(current_user, ["volunteer"]):
            raise HTTPException(
                status_code=403,
                detail="Only race organizers, volunteers, or admins can update results",
            )

    result = crud.update_race_result(
        session=session, db_result=result, result_in=result_in
    )
    return result


@router.delete("/{result_id}", response_model=Message)
def delete_race_result(
    *, session: SessionDep, current_user: CurrentUser, result_id: uuid.UUID
) -> Any:
    """
    Delete a race result.
    Only race organizers or admins can delete results.
    """
    result = crud.get_race_result(session=session, result_id=result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Race result not found")

    # Get registration to verify race
    registration = crud.get_race_registration(
        session=session, registration_id=result.registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions - only organizer or admin
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race_result(session=session, result_id=result_id)
    return Message(message="Race result deleted successfully")
