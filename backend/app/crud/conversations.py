# Placeholder for conversation and message CRUD operations 

import uuid
from typing import Sequence

from sqlmodel import Session, select, func

from app.models import (
    Conversation, ConversationCreate, User, Character,
    Message, MessageCreate, MessageSender
)


# --- Conversation CRUD ---

def create_conversation(
    *, session: Session, conversation_create: ConversationCreate, user_id: uuid.UUID
) -> Conversation:
    """Creates a new conversation between a user and a character."""
    # Validate if character exists (optional, could be done at API level too)
    character = session.get(Character, conversation_create.character_id)
    if not character:
        raise ValueError("Character not found") # Or handle appropriately

    db_obj = Conversation.model_validate(
        conversation_create, update={"user_id": user_id}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_conversation(*, session: Session, conversation_id: uuid.UUID) -> Conversation | None:
    """Gets a single conversation by its ID."""
    return session.get(Conversation, conversation_id)


def get_user_conversations(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Sequence[Conversation]:
    """Gets a list of conversations for a specific user."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    conversations = session.exec(statement).all()
    return conversations


def get_user_conversations_count(*, session: Session, user_id: uuid.UUID) -> int:
    """Gets the total count of conversations for a specific user."""
    statement = select(func.count(Conversation.id)).where(
        Conversation.user_id == user_id
    )
    count = session.exec(statement).one()
    return count


def delete_conversation(*, session: Session, db_conversation: Conversation) -> None:
    """Deletes a conversation and its associated messages (via cascade)."""
    session.delete(db_conversation)
    session.commit()


# --- Message CRUD ---

def create_message(
    *,
    session: Session,
    message_create: MessageCreate,
    conversation_id: uuid.UUID,
    sender: MessageSender,
) -> Message:
    """Adds a new message to a conversation."""
    db_obj = Message.model_validate(
        message_create, update={"conversation_id": conversation_id, "sender": sender}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_conversation_messages(
    *, session: Session, conversation_id: uuid.UUID, skip: int = 0, limit: int = 1000 # Usually get more messages
) -> Sequence[Message]:
    """Gets messages for a specific conversation, ordered by timestamp."""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
        .offset(skip)
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return messages


def get_conversation_messages_count(*, session: Session, conversation_id: uuid.UUID) -> int:
    """Gets the total count of messages for a specific conversation."""
    statement = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    count = session.exec(statement).one()
    return count 