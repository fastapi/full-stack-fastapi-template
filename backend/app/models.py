import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, model_validator
from sqlalchemy import Column, String, Text
from sqlalchemy import Enum as SQLAEnum
from sqlmodel import JSON, Field, ForeignKey, Relationship, SQLModel


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
    exams: list["Exam"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ExamBase(SQLModel):
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    duration_minutes: int | None = Field(default=None)
    is_published: bool = Field(default=False)


class Exam(ExamBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="exams")
    questions: list["Question"] = Relationship(
        back_populates="exam", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    exam_attempts: list["ExamAttempt"] = Relationship(
        back_populates="exam", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    source_document_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    difficulty: Optional["Difficulty"] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    question_types: list["QuestionType"] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExamPublic(ExamBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    questions: list["QuestionPublic"] = Field(default_factory=list)
    source_document_ids: list[str] = Field(default_factory=list)
    highest_score: float | None = Field(default=None)
    difficulty: Optional["Difficulty"] = Field(default=None)
    question_types: list["QuestionType"] = Field(default_factory=list)


class ExamsPublic(SQLModel):
    data: list[ExamPublic]
    count: int


class ExamCreate(ExamBase):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    duration_minutes: int | None = Field(
        default=None, ge=1
    )  # Must be at least 1 minute
    difficulty: Optional["Difficulty"] = None
    question_types: list["QuestionType"] = Field(default_factory=list)


class ExamUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    duration_minutes: int | None = Field(default=None, ge=1)
    is_published: bool | None = None


class QuestionType(str, Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"


class DocumentStatus(str, Enum):
    processing = "processing"
    ready = "ready"
    failed = "failed"


class QuestionBase(SQLModel):
    question: str = Field(sa_column=Column(Text, nullable=False))

    type: QuestionType = Field(
        sa_column=Column(SQLAEnum(QuestionType, native_enum=True), nullable=False)
    )

    options: list[str] = Field(sa_column=Column(JSON, nullable=False))

    # correct answer (used for grading)
    correct_answer: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )


class Question(QuestionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    exam_id: uuid.UUID = Field(foreign_key="exam.id", nullable=False)
    exam: Exam | None = Relationship(back_populates="questions")
    answers: list["Answer"] = Relationship(
        back_populates="question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# Define response model for a question
class QuestionPublic(QuestionBase):
    id: uuid.UUID
    type: QuestionType


# Properties to receive on document creation
class QuestionCreate(QuestionBase):
    type: QuestionType
    options: list[str]


class GenerateQuestionsBase(SQLModel):
    num_questions: int = Field(default=5, ge=1, le=50)
    difficulty: Optional["Difficulty"] = None
    question_types: list[QuestionType] = Field(default_factory=list)


class GenerateQuestionsPublic(GenerateQuestionsBase):
    document_ids: list[uuid.UUID]
    title: str = Field(min_length=1, max_length=255)


class ExamAttemptBase(SQLModel):
    score: float | None = None
    is_complete: bool = Field(default=False)


class AnswerExplanation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    answer_id: UUID = Field(
        sa_column=Column(
            ForeignKey("answer.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        )
    )
    explanation: str = Field(sa_column=Column(Text, nullable=False))
    key_takeaway: str = Field(sa_column=Column(Text, nullable=False))
    suggested_review: str = Field(sa_column=Column(Text, nullable=False))

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    answer: "Answer" = Relationship(back_populates="explanation")


class AnswerBase(SQLModel):
    response: str | None = None
    is_correct: bool | None = None


class ExplanationOutput(PydanticBaseModel):
    model_config = {"from_attributes": True}
    explanation: str
    key_takeaway: str
    suggested_review: str


class AnswerPublic(AnswerBase):
    id: uuid.UUID
    question_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    response: str
    is_correct: bool | None = None
    explanation: ExplanationOutput | None = None


class AnswerUpdate(SQLModel):
    id: uuid.UUID | None = None  # existing support (answer.id)
    question_id: uuid.UUID | None = None  # new support (question.id)
    response: str


class ExamAttemptPublic(ExamAttemptBase):
    # prevent string cohercion issues
    model_config = {"from_attributes": True}

    id: uuid.UUID
    exam_id: uuid.UUID
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    exam: ExamPublic | None
    answers: list[AnswerPublic]


class ExamAttemptCreate(ExamAttemptBase):
    exam_id: uuid.UUID
    answers: list["AnswerUpdate"] | None = None


class ExamAttemptUpdate(SQLModel):
    is_complete: bool | None = None
    answers: list["AnswerUpdate"] | None = None


class ExamAttempt(ExamAttemptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    exam_id: uuid.UUID = Field(
        foreign_key="exam.id", nullable=False, ondelete="CASCADE"
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    exam: Exam | None = Relationship(back_populates="exam_attempts")
    answers: list["Answer"] = Relationship(back_populates="exam_attempt")

    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class Answer(AnswerBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attempt_id: uuid.UUID = Field(foreign_key="examattempt.id", nullable=False)
    exam_attempt: "ExamAttempt" = Relationship(back_populates="answers")
    question: "Question" = Relationship(back_populates="answers")
    question_id: uuid.UUID = Field(foreign_key="question.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    explanation: AnswerExplanation | None = Relationship(
        back_populates="answer",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )


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

    status: DocumentStatus = Field(
        default=DocumentStatus.processing,
        sa_column=Column(
            SQLAEnum(DocumentStatus, name="document_status", native_enum=True),
            nullable=False,
        ),
    )

    extracted_text: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    chunks: list["DocumentChunk"] = Relationship(back_populates="document")
    chunk_count: int = 0
    processing_error: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )


class DocumentPublic(DocumentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    filename: str
    content_type: str | None = None
    size: int | None = None
    extracted_text: str | None = None
    status: DocumentStatus


class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]
    count: int


class DocumentChunkBase(SQLModel):
    text: str
    # TODO: vectorize for RAG
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(1536)))


class DocumentChunk(DocumentChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    document: Document | None = Relationship(back_populates="chunks")
    size: int = Field(ge=0)  # Number of characters in the chunk
    type: str | None = "fixed-size"


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


# Pydantic models for question items and outputs here:


class QuestionItem(PydanticBaseModel):
    question: str
    answer: str | None
    type: str
    options: list[str]  # required!

    @model_validator(mode="after")
    def validate_type_matches_options(self) -> "QuestionItem":
        """Validate and correct question type based on options.

        Also requires answer ∈ options (exact match after T/F normalization),
        matching the answer-in-options content gate used before persist/grade.
        """
        options = self.options

        # Check if options match true_false pattern
        if isinstance(options, list):
            if len(options) == 2:
                options_lower = [str(opt).strip().lower() for opt in options]
                if set(options_lower) == {"true", "false"}:
                    # Options are True/False, so type must be true_false
                    self.type = "true_false"
                    # Normalize options to ["True", "False"]
                    self.options = ["True", "False"]
            elif len(options) >= 3:
                # Options have 3+ items, so type must be multiple_choice
                self.type = "multiple_choice"

        # Final validation: ensure type matches options
        if self.type == "true_false":
            if not (
                isinstance(self.options, list)
                and len(self.options) == 2
                and {str(opt).strip().lower() for opt in self.options}
                == {"true", "false"}
            ):
                # Fix options to be ["True", "False"]
                self.options = ["True", "False"]
        elif self.type == "multiple_choice":
            if not (isinstance(self.options, list) and len(self.options) >= 3):
                raise ValueError(
                    f"Multiple choice question must have at least 3 options, got {len(self.options) if isinstance(self.options, list) else 0}"
                )

        # Correct answer must be one of the selectable options (exact membership).
        # For T/F, normalize case so "true"/"false" become "True"/"False".
        if self.answer is None:
            raise ValueError(
                "Question answer is required and must be one of the options"
            )
        if self.type == "true_false":
            answer_norm = str(self.answer).strip().lower()
            if answer_norm == "true":
                self.answer = "True"
            elif answer_norm == "false":
                self.answer = "False"
            else:
                raise ValueError(
                    f"True/false answer must be one of {self.options}, got {self.answer!r}"
                )
        elif self.answer not in self.options:
            raise ValueError(
                f"Answer must be one of the options {self.options}, got {self.answer!r}"
            )

        return self


class QuestionOutput(PydanticBaseModel):
    questions: list[QuestionItem]


# Fix forward references for all Pydantic/SQLModel models
AnswerUpdate.model_rebuild()
ExamAttemptUpdate.model_rebuild()
Answer.model_rebuild()
ExamAttempt.model_rebuild()
Question.model_rebuild()
