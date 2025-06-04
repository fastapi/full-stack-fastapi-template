import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models # Removed schemas
from app.api import deps

router = APIRouter()

# Helper function to check if user is participant or creator of the event associated with a speech
def check_event_access_for_speech(db: Session, speech_id: uuid.UUID, user: models.User) -> models.SecretSpeech:
    speech = crud.get_speech(session=db, speech_id=speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")

    event = crud.get_event(session=db, event_id=speech.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Associated event not found") # Should not happen if DB is consistent

    is_participant = any(p.user_id == user.id for p in event.participants)
    if not is_participant and event.creator_id != user.id:
        raise HTTPException(status_code=403, detail="User does not have access to the event of this speech")
    return speech

# Helper function to check if user is participant or creator of an event
def check_event_membership(db: Session, event_id: uuid.UUID, user: models.User) -> models.CoordinationEvent:
    event = crud.get_event(session=db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    is_participant = any(p.user_id == user.id for p in event.participants)
    if not is_participant and event.creator_id != user.id:
        raise HTTPException(status_code=403, detail="User must be a participant or creator of the event")
    return event


@router.post("/", response_model=models.SecretSpeechPublic, status_code=201)
def create_speech(
    *,
    db: Session = Depends(deps.get_db),
    speech_in: models.SecretSpeechWithInitialVersionCreate, # Use the new combined schema
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create a new secret speech. The current user will be set as the creator.
    An initial version of the speech is created with the provided draft.
    User must be a participant of the specified event.
    """
    # Check if user has access to the event
    event = check_event_membership(db=db, event_id=speech_in.event_id, user=current_user)
    if not event: # Should be handled by check_event_membership raising HTTPException
        raise HTTPException(status_code=404, detail="Event not found or user not participant.")

    # The SecretSpeechCreate model is currently empty, so we pass an instance.
    # The actual speech metadata (event_id, creator_id) are passed directly to crud.create_speech
    db_speech = crud.create_speech(
        session=db,
        speech_in=models.SecretSpeechCreate(), # Pass empty base model if no direct fields
        event_id=speech_in.event_id,
        creator_id=current_user.id,
        initial_draft=speech_in.initial_speech_draft,
        initial_tone=speech_in.initial_speech_tone,
        initial_duration=speech_in.initial_estimated_duration_minutes,
    )
    return db_speech


@router.get("/event/{event_id}", response_model=List[models.SecretSpeechPublic])
def list_event_speeches(
    *,
    db: Session = Depends(deps.get_db),
    event_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get all speeches for a given event. User must be a participant of the event.
    """
    check_event_membership(db=db, event_id=event_id, user=current_user)
    speeches = crud.get_event_speeches(session=db, event_id=event_id)
    return speeches


@router.get("/{speech_id}", response_model=models.SecretSpeechPublic) # Consider a more detailed model for owner
def get_speech_details(
    *,
    db: Session = Depends(deps.get_db),
    speech_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get a specific speech. User must have access to the event of this speech.
    If the user is the creator of the speech, they might get more details
    (e.g. draft of the current version - this needs handling in response shaping).
    """
    speech = check_event_access_for_speech(db=db, speech_id=speech_id, user=current_user)
    # Basic SecretSpeechPublic doesn't include version details.
    # If we want to embed current version, we'd fetch it and combine.
    # For now, returning speech metadata. API consumer can fetch versions separately.
    return speech


@router.post("/{speech_id}/versions", response_model=models.SecretSpeechVersionPublic, status_code=201)
def create_speech_version(
    *,
    db: Session = Depends(deps.get_db),
    speech_id: uuid.UUID,
    version_in: models.SecretSpeechVersionCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create a new version for a secret speech.
    User must be the creator of the speech or a participant in the event (adjust as needed).
    """
    speech = crud.get_speech(session=db, speech_id=speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")

    # Permission: only speech creator can add versions
    if speech.creator_id != current_user.id:
        # Or, check event participation if that's the rule:
        # check_event_access_for_speech(db=db, speech_id=speech_id, user=current_user)
        raise HTTPException(status_code=403, detail="Only the speech creator can add new versions.")

    new_version = crud.create_speech_version(
        session=db, version_in=version_in, speech_id=speech_id, creator_id=current_user.id
    )
    return new_version


@router.get("/{speech_id}/versions", response_model=List[models.SecretSpeechVersionPublic])
def list_speech_versions(
    *,
    db: Session = Depends(deps.get_db),
    speech_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    List all versions of a speech.
    If current user is speech creator, they see full details (including draft).
    Otherwise, they see the public version (no draft).
    """
    speech = check_event_access_for_speech(db=db, speech_id=speech_id, user=current_user)
    versions = crud.get_speech_versions(session=db, speech_id=speech_id)

    public_versions = []
    for v in versions:
        if speech.creator_id == current_user.id or v.creator_id == current_user.id: # Speech creator or version creator sees draft
            public_versions.append(models.SecretSpeechVersionDetailPublic.model_validate(v))
        else:
            public_versions.append(models.SecretSpeechVersionPublic.model_validate(v))
    return public_versions


@router.put("/{speech_id}/versions/{version_id}/set-current", response_model=models.SecretSpeechPublic)
def set_current_speech_version(
    *,
    db: Session = Depends(deps.get_db),
    speech_id: uuid.UUID,
    version_id: uuid.UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Set a specific version of a speech as the current one.
    User must be the creator of the speech.
    """
    speech = crud.get_speech(session=db, speech_id=speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")
    if speech.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the speech creator can set the current version.")

    updated_speech = crud.set_current_speech_version(
        session=db, speech_id=speech_id, version_id=version_id
    )
    if not updated_speech:
        raise HTTPException(status_code=404, detail="Version not found or does not belong to this speech.")
    return updated_speech
