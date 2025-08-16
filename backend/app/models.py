import uuid
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import Column, Text
from sqlmodel import JSON, Field, Relationship, SQLModel
from sqlmodel import Enum as SAEnum


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
    documents: list["Document"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    questions: list["Question"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class QuestionBase(SQLModel):
    question: str = Field(sa_column=Column(Text, nullable=False))
    # TODO: Get the answer from generated questions for test grading
    answer: str | None = Field(default=None, sa_column=Column(Text, nullable=True))


class Question(QuestionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    type: QuestionType = Field(
        default=QuestionType.SHORT_ANSWER,
        sa_column=Column(SAEnum(QuestionType), nullable=False),
    )
    owner: User | None = Relationship(back_populates="questions")
    options: list[str] = Field(default_factory=list, sa_column=Column(JSON))


# Define response model for a question
class QuestionPublic(QuestionBase):
    id: uuid.UUID
    owner_id: uuid.UUID

    type: QuestionType
    options: list[str] = []  # optional, only for multiple choice


# Properties to receive on document creation
class QuestionCreate(QuestionBase):
    type: QuestionType
    options: list[str] = []  # optional, only for multiple choice


class GenerateQuestionsRequest(SQLModel):
    document_ids: list[uuid.UUID]
    # maybe add difficulty, number of questions, etc.


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
