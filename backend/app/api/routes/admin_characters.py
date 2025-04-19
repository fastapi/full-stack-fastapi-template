# Placeholder for admin character management routes 

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func

from app.api.deps import SessionDep, CurrentUser, get_current_active_superuser
from app import crud
from app.models import (
    Character, CharacterUpdate, CharacterPublic, CharactersPublic, CharacterStatus, Message
)

router = APIRouter(prefix="/admin/characters", tags=["admin-characters"],
                   dependencies=[Depends(get_current_active_superuser)])


@router.get("/", response_model=CharactersPublic)
def list_all_characters(
    session: SessionDep, skip: int = 0, limit: int = 100, status: CharacterStatus | None = None
) -> Any:
    """
    Retrieve all characters (admin view).
    Optionally filter by status.
    """
    count = crud.characters.get_characters_count(session=session, status=status)
    characters = crud.characters.get_characters(
        session=session, skip=skip, limit=limit, status=status
    )
    return CharactersPublic(data=characters, count=count)


@router.get("/pending", response_model=CharactersPublic)
def list_pending_characters(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve characters pending approval.
    """
    count = crud.characters.get_characters_count(session=session, status=CharacterStatus.PENDING)
    characters = crud.characters.get_characters(
        session=session, skip=skip, limit=limit, status=CharacterStatus.PENDING
    )
    return CharactersPublic(data=characters, count=count)


@router.patch("/{id}/approve", response_model=CharacterPublic)
def approve_character(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Approve a character submission.
    """
    db_character = crud.characters.get_character(session=session, character_id=id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    if db_character.status != CharacterStatus.PENDING:
        raise HTTPException(status_code=400, detail="Character is not pending approval")

    character_update = CharacterUpdate(status=CharacterStatus.APPROVED)
    character = crud.characters.update_character(
        session=session, db_character=db_character, character_in=character_update
    )
    return character


@router.patch("/{id}/reject", response_model=CharacterPublic)
def reject_character(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Reject a character submission.
    """
    db_character = crud.characters.get_character(session=session, character_id=id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    if db_character.status != CharacterStatus.PENDING:
        raise HTTPException(status_code=400, detail="Character is not pending approval")

    character_update = CharacterUpdate(status=CharacterStatus.REJECTED)
    character = crud.characters.update_character(
        session=session, db_character=db_character, character_in=character_update
    )
    return character


@router.put("/{id}", response_model=CharacterPublic)
def update_character_admin(
    *, session: SessionDep, id: uuid.UUID, character_in: CharacterUpdate
) -> Any:
    """
    Update any character (admin only).
    """
    db_character = crud.characters.get_character(session=session, character_id=id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    character = crud.characters.update_character(
        session=session, db_character=db_character, character_in=character_in
    )
    return character


@router.delete("/{id}")
def delete_character_admin(
    session: SessionDep, id: uuid.UUID
) -> Message:
    """
    Delete a character (admin only).
    """
    db_character = crud.characters.get_character(session=session, character_id=id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    crud.characters.delete_character(session=session, db_character=db_character)
    return Message(message="Character deleted successfully") 