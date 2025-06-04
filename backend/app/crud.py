import uuid
from typing import Any

from sqlmodel import Session, select, func # Added func

from app.core.security import get_password_hash, verify_password
from app.models import ( # Updated imports
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
    CoordinationEvent,
    CoordinationEventCreate,
    EventParticipant,
    EventParticipantCreate,
    SecretSpeech,
    SecretSpeechCreate,
    SecretSpeechVersion,
    SecretSpeechVersionCreate,
    UserPublic, # Added for get_event_participants
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# CoordinationEvent CRUD
def create_event(
    *, session: Session, event_in: CoordinationEventCreate, creator_id: uuid.UUID
) -> CoordinationEvent:
    db_event = CoordinationEvent.model_validate(event_in, update={"creator_id": creator_id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    # Add creator as the first participant
    add_event_participant(
        session=session, event_id=db_event.id, user_id=creator_id, role="creator"
    )
    session.refresh(db_event) # Refresh to get updated participants list
    return db_event


def get_event(*, session: Session, event_id: uuid.UUID) -> CoordinationEvent | None:
    statement = select(CoordinationEvent).where(CoordinationEvent.id == event_id)
    return session.exec(statement).first()


def get_user_events(*, session: Session, user_id: uuid.UUID) -> list[CoordinationEvent]:
    statement = (
        select(CoordinationEvent)
        .join(EventParticipant)
        .where(EventParticipant.user_id == user_id)
    )
    return session.exec(statement).all()


def add_event_participant(
    *, session: Session, event_id: uuid.UUID, user_id: uuid.UUID, role: str = "participant"
) -> EventParticipant | None:
    # Check if event and user exist
    event = get_event(session=session, event_id=event_id)
    if not event:
        return None
    # TODO: Check if user exists (assuming user_id is validated upstream or by DB)

    # Check if participant already exists
    existing_participant_statement = select(EventParticipant).where(
        EventParticipant.event_id == event_id, EventParticipant.user_id == user_id
    )
    if session.exec(existing_participant_statement).first():
        return None  # Or raise an exception/return existing

    participant_in = EventParticipantCreate(event_id=event_id, user_id=user_id, role=role)
    db_participant = EventParticipant.model_validate(participant_in)
    session.add(db_participant)
    session.commit()
    session.refresh(db_participant)
    return db_participant


def remove_event_participant(
    *, session: Session, event_id: uuid.UUID, user_id: uuid.UUID
) -> EventParticipant | None:
    statement = select(EventParticipant).where(
        EventParticipant.event_id == event_id, EventParticipant.user_id == user_id
    )
    participant_to_delete = session.exec(statement).first()
    if participant_to_delete:
        session.delete(participant_to_delete)
        session.commit()
        return participant_to_delete
    return None


def get_event_participants(*, session: Session, event_id: uuid.UUID) -> list[UserPublic]:
    statement = (
        select(User)
        .join(EventParticipant)
        .where(EventParticipant.event_id == event_id)
    )
    users = session.exec(statement).all()
    return [UserPublic.model_validate(user) for user in users]


# SecretSpeech CRUD
def create_speech(
    *,
    session: Session,
    speech_in: SecretSpeechCreate,
    event_id: uuid.UUID,
    creator_id: uuid.UUID,
    initial_draft: str,
    initial_tone: str = "neutral", # Default tone
    initial_duration: int = 5, # Default duration in minutes
) -> SecretSpeech:
    db_speech = SecretSpeech.model_validate(
        speech_in, update={"event_id": event_id, "creator_id": creator_id}
    )
    session.add(db_speech)
    session.commit()
    session.refresh(db_speech)

    # Create initial SecretSpeechVersion
    version_in = SecretSpeechVersionCreate(
        speech_draft=initial_draft,
        speech_tone=initial_tone,
        estimated_duration_minutes=initial_duration,
    )
    # Note: create_speech_version handles version_number automatically
    initial_version = create_speech_version(
        session=session, version_in=version_in, speech_id=db_speech.id, creator_id=creator_id
    )

    # Set current_version_id
    db_speech.current_version_id = initial_version.id
    session.add(db_speech)
    session.commit()
    session.refresh(db_speech)
    return db_speech


def get_speech(*, session: Session, speech_id: uuid.UUID) -> SecretSpeech | None:
    statement = select(SecretSpeech).where(SecretSpeech.id == speech_id)
    return session.exec(statement).first()


def get_event_speeches(*, session: Session, event_id: uuid.UUID) -> list[SecretSpeech]:
    statement = select(SecretSpeech).where(SecretSpeech.event_id == event_id)
    return session.exec(statement).all()


# SecretSpeechVersion CRUD
def create_speech_version(
    *,
    session: Session,
    version_in: SecretSpeechVersionCreate,
    speech_id: uuid.UUID,
    creator_id: uuid.UUID,
) -> SecretSpeechVersion:
    # Determine next version_number
    current_max_version_statement = select(func.max(SecretSpeechVersion.version_number)).where(
        SecretSpeechVersion.speech_id == speech_id
    )
    max_version = session.exec(current_max_version_statement).one_or_none()
    next_version_number = (max_version + 1) if max_version is not None else 1

    db_version = SecretSpeechVersion.model_validate(
        version_in,
        update={
            "speech_id": speech_id,
            "creator_id": creator_id,
            "version_number": next_version_number,
        },
    )
    session.add(db_version)
    session.commit()
    session.refresh(db_version)
    return db_version


def get_speech_versions(
    *, session: Session, speech_id: uuid.UUID
) -> list[SecretSpeechVersion]:
    statement = (
        select(SecretSpeechVersion)
        .where(SecretSpeechVersion.speech_id == speech_id)
        .order_by(SecretSpeechVersion.version_number) # Or .order_by(SecretSpeechVersion.created_at)
    )
    return session.exec(statement).all()


def get_speech_version(
    *, session: Session, version_id: uuid.UUID
) -> SecretSpeechVersion | None:
    statement = select(SecretSpeechVersion).where(SecretSpeechVersion.id == version_id)
    return session.exec(statement).first()


def set_current_speech_version(
    *, session: Session, speech_id: uuid.UUID, version_id: uuid.UUID
) -> SecretSpeech | None:
    speech = get_speech(session=session, speech_id=speech_id)
    if not speech:
        return None

    version = get_speech_version(session=session, version_id=version_id)
    if not version or version.speech_id != speech_id:
        # Ensure the version belongs to this speech
        return None

    speech.current_version_id = version_id
    session.add(speech)
    session.commit()
    session.refresh(speech)
    return speech
