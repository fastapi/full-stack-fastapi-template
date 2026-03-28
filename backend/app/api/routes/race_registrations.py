import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    RaceCategoryPublic,
    RaceRegistrationCreate,
    RaceRegistrationPublic,
    RaceRegistrationPublicWithDetails,
    RaceRegistrationsPublic,
    RaceRegistrationUpdate,
    User,
    UserPublic,
)

router = APIRouter(prefix="/race-registrations", tags=["race-registrations"])


@router.get("/", response_model=RaceRegistrationsPublic)
def read_race_registrations(
    session: SessionDep,
    current_user: CurrentUser,
    race_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve race registrations.
    - Runners see only their own registrations
    - Organizers see registrations for their races
    - Admins see all registrations
    """
    if current_user.is_superuser:
        # Admin sees all
        registrations = crud.get_race_registrations(
            session=session,
            race_id=race_id,
            category_id=category_id,
            skip=skip,
            limit=limit,
        )
        count = crud.get_race_registrations_count(
            session=session, race_id=race_id, category_id=category_id
        )
    elif crud.user_has_any_role(current_user, ["organizer"]):
        # Organizer sees registrations for their races
        if race_id:
            race = crud.get_race(session=session, race_id=race_id)
            if not race or race.organizer_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only view registrations for your own races",
                )
        registrations = crud.get_race_registrations(
            session=session,
            race_id=race_id,
            category_id=category_id,
            skip=skip,
            limit=limit,
        )
        count = crud.get_race_registrations_count(
            session=session, race_id=race_id, category_id=category_id
        )
    else:
        # Runner sees only their own registrations
        registrations = crud.get_race_registrations(
            session=session,
            race_id=race_id,
            runner_id=current_user.id,
            category_id=category_id,
            skip=skip,
            limit=limit,
        )
        count = crud.get_race_registrations_count(
            session=session,
            race_id=race_id,
            runner_id=current_user.id,
            category_id=category_id,
        )

    registrations_public = [
        RaceRegistrationPublic.model_validate(reg) for reg in registrations
    ]
    return RaceRegistrationsPublic(data=registrations_public, count=count)


@router.get("/my", response_model=RaceRegistrationsPublic)
def read_my_registrations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve current user's race registrations.
    """
    registrations = crud.get_race_registrations(
        session=session, runner_id=current_user.id, skip=skip, limit=limit
    )
    count = crud.get_race_registrations_count(
        session=session, runner_id=current_user.id
    )
    registrations_public = [
        RaceRegistrationPublic.model_validate(reg) for reg in registrations
    ]
    return RaceRegistrationsPublic(data=registrations_public, count=count)


@router.get("/{registration_id}", response_model=RaceRegistrationPublicWithDetails)
def read_race_registration(
    session: SessionDep, current_user: CurrentUser, registration_id: uuid.UUID
) -> Any:
    """
    Get race registration by ID with details.
    """
    registration = crud.get_race_registration(
        session=session, registration_id=registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    if (
        not current_user.is_superuser
        and registration.runner_id != current_user.id
        and race.organizer_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Get related data
    runner = session.get(User, registration.runner_id)
    if not runner:
        raise HTTPException(status_code=404, detail="Runner not found")

    category = crud.get_race_category(
        session=session, category_id=registration.category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return RaceRegistrationPublicWithDetails(
        **registration.model_dump(),
        runner=UserPublic.model_validate(runner),
        category=RaceCategoryPublic.model_validate(category),
    )


@router.post("/", response_model=RaceRegistrationPublic)
def create_race_registration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    registration_in: RaceRegistrationCreate,
) -> Any:
    """
    Create new race registration.
    Runners can register themselves for races.
    """
    # Check if race and category exist
    race = crud.get_race(session=session, race_id=registration_in.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    category = crud.get_race_category(
        session=session, category_id=registration_in.category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")

    # Verify category belongs to race
    if category.race_id != race.id:
        raise HTTPException(
            status_code=400, detail="Category does not belong to this race"
        )

    # Check if already registered
    existing_registration = crud.check_existing_registration(
        session=session, runner_id=current_user.id, race_id=race.id
    )
    if existing_registration:
        raise HTTPException(
            status_code=400, detail="You are already registered for this race"
        )

    # Check if registration is open
    if not crud.is_category_registration_open(
        category=category, race=race, session=session
    ):
        raise HTTPException(
            status_code=400, detail="Registration is not open for this category"
        )

    # Create registration
    registration = crud.create_race_registration(
        session=session, registration_in=registration_in, runner_id=current_user.id
    )
    return registration


@router.put("/{registration_id}", response_model=RaceRegistrationPublic)
def update_race_registration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    registration_id: uuid.UUID,
    registration_in: RaceRegistrationUpdate,
) -> Any:
    """
    Update a race registration.
    - Runners can update their own registration details
    - Organizers can update any field for their races
    - Admins can update anything
    """
    registration = crud.get_race_registration(
        session=session, registration_id=registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    is_own_registration = registration.runner_id == current_user.id
    is_race_organizer = race.organizer_id == current_user.id

    if (
        not current_user.is_superuser
        and not is_own_registration
        and not is_race_organizer
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Runners can only update certain fields
    if is_own_registration and not is_race_organizer and not current_user.is_superuser:
        # Restrict what runners can update
        restricted_fields = {
            "emergency_contact",
            "emergency_phone",
            "tshirt_size",
            "special_requirements",
        }
        update_data = registration_in.model_dump(exclude_unset=True)
        if any(field not in restricted_fields for field in update_data.keys()):
            raise HTTPException(
                status_code=403,
                detail="You can only update your personal information",
            )

    registration = crud.update_race_registration(
        session=session, db_registration=registration, registration_in=registration_in
    )
    return registration


@router.delete("/{registration_id}", response_model=Message)
def delete_race_registration(
    *, session: SessionDep, current_user: CurrentUser, registration_id: uuid.UUID
) -> Any:
    """
    Delete/Cancel a race registration.
    - Runners can cancel their own registrations
    - Organizers can cancel registrations for their races
    - Admins can cancel any registration
    """
    registration = crud.get_race_registration(
        session=session, registration_id=registration_id
    )
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=registration.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if (
        not current_user.is_superuser
        and registration.runner_id != current_user.id
        and race.organizer_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race_registration(session=session, registration_id=registration_id)
    return Message(message="Registration cancelled successfully")
