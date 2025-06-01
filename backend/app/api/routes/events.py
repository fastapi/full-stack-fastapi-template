import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session

from app import crud, models # Removed schemas
from app.api import deps
from app.services import speech_analysis_service

router = APIRouter()


@router.post("/", response_model=models.CoordinationEventPublic, status_code=201)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: models.CoordinationEventCreate,
    current_user: deps.CurrentUser,
) -> models.CoordinationEvent:
    """
    Create a new coordination event.
    The current user will be set as the creator and an initial participant.
    """
    event = crud.create_event(session=db, event_in=event_in, creator_id=current_user.id)
    return event


@router.get("/", response_model=List[models.CoordinationEventPublic])
def list_user_events(
    *,
    db: Session = Depends(deps.get_db),
    current_user: deps.CurrentUser,
) -> Any:
    """
    List all events the current user is participating in.
    """
    events = crud.get_user_events(session=db, user_id=current_user.id)
    return events


@router.get("/{event_id}", response_model=models.CoordinationEventPublic)
def get_event_details(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get details of a specific event. User must be a participant.
    """
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if current user is a participant
    is_participant = any(p.user_id == current_user.id for p in event.participants)
    if not is_participant and event.creator_id != current_user.id: # Creator also has access
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return event


@router.post("/{event_id}/participants", response_model=models.EventParticipantPublic)
def add_event_participant(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    user_id_to_add: uuid.UUID = Body(..., embed=True),
    role: str = Body("participant", embed=True),
    current_user: deps.CurrentUser,
) -> Any:
    """
    Add a user to an event. Only the event creator can add participants.
    """
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the event creator can add participants")

    # Check if user to add exists (optional, DB will catch it if not)
    user_to_add = db.get(models.User, user_id_to_add)
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User to add not found")

    participant = crud.add_event_participant(
        session=db, event_id=event_id, user_id=user_id_to_add, role=role
    )
    if not participant:
        raise HTTPException(status_code=400, detail="Participant already in event or other error")
    return participant


@router.delete("/{event_id}/participants/{user_id_to_remove}", response_model=models.Message)
def remove_event_participant(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    user_id_to_remove: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Remove a participant from an event.
    Allowed if:
    - Current user is the event creator.
    - Current user is removing themselves.
    """
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    is_creator = event.creator_id == current_user.id
    is_self_removal = user_id_to_remove == current_user.id

    if not (is_creator or is_self_removal):
        raise HTTPException(status_code=403, detail="Not enough permissions to remove participant")

    # Prevent creator from being removed by themselves if they are the last participant (or handle elsewhere)
    if is_self_removal and is_creator and len(event.participants) == 1:
        raise HTTPException(status_code=400, detail="Creator cannot remove themselves if they are the last participant. Delete the event instead.")


    removed_participant = crud.remove_event_participant(
        session=db, event_id=event_id, user_id=user_id_to_remove
    )
    if not removed_participant:
        raise HTTPException(status_code=404, detail="Participant not found in this event")
    return models.Message(message="Participant removed successfully")


@router.get("/{event_id}/participants", response_model=List[models.UserPublic])
def list_event_participants(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    List participants of an event. User must be a participant of the event.
    """
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    is_participant = any(p.user_id == current_user.id for p in event.participants)
    if not is_participant and event.creator_id != current_user.id:
         raise HTTPException(status_code=403, detail="User must be a participant to view other participants")

    participants = crud.get_event_participants(session=db, event_id=event_id)
    return participants


@router.get("/{event_id}/speech-analysis", response_model=List[models.PersonalizedNudgePublic])
def get_event_speech_analysis(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Perform analysis on speeches within an event and return personalized nudges
    for the current user. User must be a participant of the event.
    """
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if current user is a participant or creator
    is_participant = any(p.user_id == current_user.id for p in event.participants)
    if not is_participant and event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="User must be a participant or creator to access speech analysis.")

    all_event_nudges = speech_analysis_service.analyse_event_speeches(db=db, event_id=event_id)

    # Filter nudges for the current user
    user_nudges = [
        models.PersonalizedNudgePublic(
            nudge_type=n.nudge_type,
            message=n.message,
            severity=n.severity
        )
        for n in all_event_nudges if n.user_id == current_user.id
    ]

    return user_nudges
