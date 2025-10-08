import uuid

from pydantic import EmailStr
from sqlalchemy import Column, Text
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
    documents: list["Document"] = Relationship(
        back_populates="owner", cascade_delete=True
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


# Shared properties
class DocumentBase(SQLModel):
    filename: str = Field(min_length=1, max_length=255)
    s3_url: str | None = Field(
        default=None, max_length=255
    )  # URL to the document in S3
    s3_key: str | None = Field(default=None, max_length=1024)
    content_type: str | None = Field(default=None, max_length=255)
    size: int | None = Field(default=None, ge=0)  # Size in bytes


# Properties to receive on document creation
class DocumentCreate(DocumentBase):
    pass


# Properties to receive on document update
class DocumentUpdate(DocumentBase):
    filename: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="documents")
    extracted_text: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    chunks: list["DocumentChunk"] = Relationship(back_populates="document")
    chunk_count: int = 0  # Number of chunks created for this document


class DocumentPublic(DocumentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    filename: str
    content_type: str | None = None
    size: int | None = None
    extracted_text: str | None = None


class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]
    count: int


class DocumentChunkBase(SQLModel):
    text: str
    # TODO: vectorize for RAG
    # vector: list[float] | None = Field(default=None, sa_column=Column(Vector(1536)))


class DocumentChunk(DocumentChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    document: Document | None = Relationship(back_populates="chunks")
    size: int = Field(ge=0)  # Number of characters in the chunk
    type: str | None = "fixed-size"


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
