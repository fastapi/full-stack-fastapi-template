import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    RaceAttributeCreate,
    RaceAttributePublic,
    RaceAttributesPublic,
    RaceAttributeUpdate,
)

router = APIRouter(prefix="/race-attributes", tags=["race-attributes"])


@router.get("/", response_model=RaceAttributesPublic)
def read_race_attributes(
    session: SessionDep,
    race_id: uuid.UUID,
    is_public: bool | None = None,
) -> Any:
    """
    Retrieve race attributes for a specific race.
    Public endpoint - filters by is_public by default unless authenticated organizer/admin.
    """
    attributes = crud.get_race_attributes(
        session=session, race_id=race_id, is_public=is_public
    )
    attributes_public = [
        RaceAttributePublic.model_validate(attr) for attr in attributes
    ]
    return RaceAttributesPublic(data=attributes_public, count=len(attributes_public))


@router.get("/{attribute_id}", response_model=RaceAttributePublic)
def read_race_attribute(session: SessionDep, attribute_id: uuid.UUID) -> Any:
    """
    Get race attribute by ID.
    """
    attribute = crud.get_race_attribute(session=session, attribute_id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Race attribute not found")
    return attribute


@router.post("/", response_model=RaceAttributePublic)
def create_race_attribute(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    attribute_in: RaceAttributeCreate,
) -> Any:
    """
    Create new race attribute.
    Only the race organizer or admin can create attributes.
    """
    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=attribute_in.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    attribute = crud.create_race_attribute(session=session, attribute_in=attribute_in)
    return attribute


@router.put("/{attribute_id}", response_model=RaceAttributePublic)
def update_race_attribute(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    attribute_id: uuid.UUID,
    attribute_in: RaceAttributeUpdate,
) -> Any:
    """
    Update a race attribute.
    Only the race organizer or admin can update.
    """
    attribute = crud.get_race_attribute(session=session, attribute_id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Race attribute not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=attribute.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    attribute = crud.update_race_attribute(
        session=session, db_attribute=attribute, attribute_in=attribute_in
    )
    return attribute


@router.delete("/{attribute_id}", response_model=Message)
def delete_race_attribute(
    *, session: SessionDep, current_user: CurrentUser, attribute_id: uuid.UUID
) -> Any:
    """
    Delete a race attribute.
    Only the race organizer or admin can delete.
    """
    attribute = crud.get_race_attribute(session=session, attribute_id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Race attribute not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=attribute.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race_attribute(session=session, attribute_id=attribute_id)
    return Message(message="Race attribute deleted successfully")
