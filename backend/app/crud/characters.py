# Placeholder for character CRUD operations 

import uuid
from typing import Sequence

from sqlmodel import Session, select, col, func

from app.models import Character, CharacterCreate, CharacterUpdate, CharacterStatus, User


def create_character(
    *, session: Session, character_create: CharacterCreate, creator_id: uuid.UUID
) -> Character:
    """Creates a new character with status 'pending'."""
    db_obj = Character.model_validate(
        character_create, update={"creator_id": creator_id, "status": CharacterStatus.PENDING}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_character(*, session: Session, character_id: uuid.UUID) -> Character | None:
    """Gets a single character by its ID."""
    return session.get(Character, character_id)


def get_characters(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    status: CharacterStatus | None = None,
    creator_id: uuid.UUID | None = None,
) -> Sequence[Character]:
    """Gets a list of characters with optional filters."""
    statement = select(Character).offset(skip).limit(limit)
    if status is not None:
        statement = statement.where(Character.status == status)
    if creator_id is not None:
        statement = statement.where(Character.creator_id == creator_id)

    characters = session.exec(statement).all()
    return characters


def get_characters_count(
    *,
    session: Session,
    status: CharacterStatus | None = None,
    creator_id: uuid.UUID | None = None,
) -> int:
    """Gets the total count of characters with optional filters."""
    statement = select(func.count(Character.id))
    if status is not None:
        statement = statement.where(Character.status == status)
    if creator_id is not None:
        statement = statement.where(Character.creator_id == creator_id)

    count = session.exec(statement).one()
    return count


def update_character(
    *, session: Session, db_character: Character, character_in: CharacterUpdate
) -> Character:
    """Updates an existing character."""
    update_data = character_in.model_dump(exclude_unset=True)
    db_character.sqlmodel_update(update_data)
    session.add(db_character)
    session.commit()
    session.refresh(db_character)
    return db_character


def delete_character(*, session: Session, db_character: Character) -> None:
    """Deletes a character."""
    # Add cascade delete for conversations/messages if needed, handled by relationship cascade
    session.delete(db_character)
    session.commit() 