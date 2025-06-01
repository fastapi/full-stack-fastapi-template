import uuid
from datetime import datetime # Added
from typing import List, Optional # Added

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel # Removed sa_column_kwargs from import


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    coordinated_events: List["CoordinationEvent"] = Relationship(back_populates="creator") # Added
    event_participations: List["EventParticipant"] = Relationship(back_populates="user") # Added
    created_speeches: List["SecretSpeech"] = Relationship(back_populates="creator") # Added
    created_speech_versions: List["SecretSpeechVersion"] = Relationship(back_populates="creator") # Added


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# CoordinationEvent
class CoordinationEventBase(SQLModel):
    event_type: str
    event_name: str
    event_date: datetime


class CoordinationEventCreate(CoordinationEventBase):
    pass


class CoordinationEventUpdate(SQLModel):
    event_type: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[datetime] = None


class CoordinationEvent(CoordinationEventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    creator: "User" = Relationship(back_populates="coordinated_events")
    participants: List["EventParticipant"] = Relationship(back_populates="event", cascade_delete=True)
    secret_speeches: List["SecretSpeech"] = Relationship(back_populates="event", cascade_delete=True)


class CoordinationEventPublic(CoordinationEventBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# EventParticipant
class EventParticipantBase(SQLModel):
    role: str
    user_id: uuid.UUID = Field(foreign_key="user.id")
    event_id: uuid.UUID = Field(foreign_key="coordinationevent.id")


class EventParticipantCreate(EventParticipantBase):
    pass


class EventParticipant(EventParticipantBase, table=True):
    __tablename__ = "event_participant" # Explicit table name for association table
    event_id: uuid.UUID = Field(foreign_key="coordinationevent.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    event: CoordinationEvent = Relationship(back_populates="participants")
    user: "User" = Relationship(back_populates="event_participations")


class EventParticipantPublic(SQLModel):
    user_id: uuid.UUID
    event_id: uuid.UUID
    role: str
    added_at: datetime


# SecretSpeech
class SecretSpeechBase(SQLModel):
    pass # Add fields if there are any common editable fields not related to versioning


class SecretSpeechCreate(SecretSpeechBase):
    # Typically, the first version's content would be part of this
    # or handled in a service layer that creates speech and its first version.
    # This schema is for the DB model, API creation might use a different one (see below)
    pass


# Schema for creating a SecretSpeech along with its first version via API
class SecretSpeechWithInitialVersionCreate(SecretSpeechBase): # Inherits any base fields from SecretSpeechBase
    event_id: uuid.UUID
    # Initial version fields
    initial_speech_draft: str
    initial_speech_tone: str = "neutral"
    initial_estimated_duration_minutes: int = 5


class SecretSpeechUpdate(SQLModel):
    # e.g., for changing metadata if any, or current_version_id
    current_version_id: Optional[uuid.UUID] = None


class SecretSpeech(SecretSpeechBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="coordinationevent.id")
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    # Using Optional[uuid.UUID] and sa_column_kwargs={"defer": True} is not directly supported by SQLModel for FKs in this way.
    # Instead, ensure SecretSpeechVersion is defined or use forward reference if needed.
    # For now, making it nullable. If it's an FK, it needs a target.
    current_version_id: uuid.UUID | None = Field(default=None, foreign_key="secretspeechversion.id", nullable=True) # Deferring not standard in SQLModel like in pure SQLAlchemy
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    event: CoordinationEvent = Relationship(back_populates="secret_speeches")
    creator: "User" = Relationship(back_populates="created_speeches")
    versions: List["SecretSpeechVersion"] = Relationship(back_populates="speech", cascade_delete=True)
    # current_version: Optional["SecretSpeechVersion"] = Relationship(sa_relationship_kwargs={'foreign_keys': '[SecretSpeech.current_version_id]', 'lazy': 'joined'}) # This is more complex with SQLModel


class SecretSpeechPublic(SecretSpeechBase):
    id: uuid.UUID
    event_id: uuid.UUID
    creator_id: uuid.UUID
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# SecretSpeechVersion
class SecretSpeechVersionBase(SQLModel):
    speech_draft: str # Sensitive, not in public by default
    speech_tone: str
    estimated_duration_minutes: int


class SecretSpeechVersionCreate(SecretSpeechVersionBase):
    pass


class SecretSpeechVersion(SecretSpeechVersionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    speech_id: uuid.UUID = Field(foreign_key="secretspeech.id")
    version_number: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    creator_id: uuid.UUID = Field(foreign_key="user.id") # To track who created this version

    speech: SecretSpeech = Relationship(back_populates="versions")
    creator: "User" = Relationship(back_populates="created_speech_versions")


class SecretSpeechVersionPublic(SQLModel):
    id: uuid.UUID
    speech_id: uuid.UUID
    version_number: int
    # speech_draft is excluded for non-owner/creator
    speech_tone: str
    estimated_duration_minutes: int
    created_at: datetime
    creator_id: uuid.UUID # Consider if this should be exposed, or just creator's public info


# More nuanced SecretSpeechVersionPublic for owners to see draft
class SecretSpeechVersionDetailPublic(SecretSpeechVersionPublic):
    speech_draft: str


# PersonalizedNudge Schemas
class PersonalizedNudgeBase(SQLModel):
    nudge_type: str # e.g., "tone_mismatch", "keyword_overlap", "length_discrepancy"
    message: str    # The actual advice
    severity: str   # e.g., "info", "warning"

# This is the public version of the nudge, intended for API responses.
# It does not include user_id because the endpoint will filter for the current user.
class PersonalizedNudgePublic(PersonalizedNudgeBase):
    pass # Inherits all fields from PersonalizedNudgeBase

# If we were to store nudges, we might have a PersonalizedNudgeDB model here.
# For now, PersonalizedNudge will be an internal dataclass in the service.
