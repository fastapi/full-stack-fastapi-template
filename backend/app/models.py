import uuid
import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


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
    created_characters: list["Character"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    conversations: list["Conversation"] = Relationship(
        back_populates="user", cascade_delete=True
    )


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

# ------------------------Character Model----------------------------

# Shared properties
class CharacterBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=255)
    greeting_message: str | None = Field(default=None, max_length=1000)
# More field
    scenario: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=255)
    greeting: str | None = Field(default=None, max_length=1000)
    voice_id: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = Field(default=None)
    popularity_score: float | None = Field(default=None)
    is_featured: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CharacterStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Properties to receive via API on creation (user submission)
class CharacterCreate(CharacterBase):
    pass


# Properties to receive via API on update (admin only)
class CharacterUpdate(CharacterBase):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=255)
    greeting_message: str | None = Field(default=None, max_length=1000)
# More fields
    scenario: str | None = Field(default=None, max_length=2000)
    greeting: str | None = Field(default=None, max_length=1000)
    category: str | None = Field(default=None, max_length=255)
    voice_id: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = Field(default=None)
    popularity_score: float | None = Field(default=0.0)
    is_featured: bool = Field(default=False)
    created_at: datetime | None = None

    status: CharacterStatus | None = None


# Database model
class Character(CharacterBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    status: CharacterStatus = Field(default=CharacterStatus.PENDING)
    like_count: int = Field(default=0)
    total_messages: int = Field(default=0) 

    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    creator: User = Relationship(back_populates="created_characters")
    conversations: list["Conversation"] = Relationship(back_populates="character")

# Properties to return via API
class CharacterPublic(CharacterBase):
    id: uuid.UUID
    status: CharacterStatus
    creator_id: uuid.UUID

    like_count: int
    total_messages: int
    created_at: datetime


class CharactersPublic(SQLModel):
    data: list[CharacterPublic]
    count: int


# ---------------- Conversation Models ----------------


class ConversationBase(SQLModel):
    pass  # No shared fields initially, maybe add title later?


class ConversationCreate(SQLModel):
    character_id: uuid.UUID


# Database model
class Conversation(ConversationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    character_id: uuid.UUID = Field(foreign_key="character.id", nullable=False)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    user: User = Relationship(back_populates="conversations")
    character: Character = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")


class ConversationPublic(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    character_id: uuid.UUID
    created_at: datetime.datetime


class ConversationsPublic(SQLModel):
    data: list[ConversationPublic]
    count: int


# ---------------- Message Models ----------------


class MessageSender(str, Enum):
    USER = "user"
    AI = "ai"


class MessageBase(SQLModel):
    content: str = Field(max_length=5000)  # Limit message length


class MessageCreate(MessageBase):
    pass  # Content is the main input


# Database model
class Message(MessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", nullable=False)
    sender: MessageSender
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")


class MessagePublic(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender: MessageSender
    timestamp: datetime.datetime


class MessagesPublic(SQLModel):
    data: list[MessagePublic]
    count: int
