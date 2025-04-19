# Placeholder for character submission and listing routes 

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func

from app.api.deps import SessionDep, CurrentUser
from app import crud
from app.models import (
    Character, CharacterCreate, CharacterPublic, CharactersPublic, CharacterStatus, Message
)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=CharactersPublic)
def list_approved_characters(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve approved characters.
    """
    count = crud.characters.get_characters_count(
        session=session, status=CharacterStatus.APPROVED
    )
    characters = crud.characters.get_characters(
        session=session, skip=skip, limit=limit, status=CharacterStatus.APPROVED
    )
    return CharactersPublic(data=characters, count=count)


@router.get("/{id}", response_model=CharacterPublic)
def get_approved_character(
    session: SessionDep, id: uuid.UUID
) -> Any:
    """
    Get a specific approved character by ID.
    """
    character = crud.characters.get_character(session=session, character_id=id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    if character.status != CharacterStatus.APPROVED:
        # Hide non-approved characters from this public endpoint
        raise HTTPException(status_code=404, detail="Character not found") # Or 403 Forbidden
    return character


@router.post("/submit", response_model=CharacterPublic, status_code=201)
def submit_character(
    *, session: SessionDep, current_user: CurrentUser, character_in: CharacterCreate
) -> Any:
    """
    Submit a new character for review.
    Status defaults to 'pending'.
    """
    character = crud.characters.create_character(
        session=session, character_create=character_in, creator_id=current_user.id
    )
    return character 