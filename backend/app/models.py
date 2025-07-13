import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from sqlalchemy import UniqueConstraint


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: str = Field(default="user", max_length=20)  # "user", "trainer", "counselor", "admin", "super_admin"


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)
    role: str | None = Field(default=None, max_length=20)  # Allow role updates by admin


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
    role: str = Field(default="user", max_length=20)  # "user", "trainer", "counselor", "admin", "super_admin"
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="SET NULL"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    ai_souls: list["AISoulEntity"] = Relationship(back_populates="user", cascade_delete=True)
    organization: Optional["Organization"] = Relationship(back_populates="users")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    role: str
    created_at: datetime
    updated_at: datetime


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


# Chat Message models
class ChatMessageBase(SQLModel):
    content: str = Field(min_length=1, max_length=5000)


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    is_from_user: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship()
    ai_soul: Optional["AISoulEntity"] = Relationship(back_populates="chat_messages")


class ChatMessagePublic(ChatMessageBase):
    id: uuid.UUID | None  # None for temporary messages
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    is_from_user: bool
    timestamp: datetime
    is_temporary: bool = False  # Flag to indicate temporary "under review" messages


# Document/PDF models for RAG
class DocumentBase(SQLModel):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_size: int
    content_type: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    file_path: str = Field(max_length=500)
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: str = Field(default="pending", max_length=50)
    chunk_count: int = Field(default=0)
    user: User | None = Relationship()


class DocumentPublic(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    upload_timestamp: datetime
    processing_status: str
    chunk_count: int


# Document chunks for RAG embeddings
class DocumentChunkBase(SQLModel):
    content: str = Field(min_length=1, max_length=2000)
    chunk_index: int
    chunk_metadata: str | None = Field(default=None, max_length=1000)


class DocumentChunk(DocumentChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    embedding: str | None = Field(default=None, max_length=50000)  # JSON string of embedding vector
    created_at: datetime = Field(default_factory=datetime.utcnow)
    document: Document | None = Relationship()


class DocumentChunkPublic(DocumentChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]
    count: int


# AI Soul Entity models
class AISoulEntityBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    persona_type: str = Field(max_length=50)  # e.g., counselor, mentor, coach
    specializations: str = Field(max_length=500)  # Comma-separated list of specialties
    base_prompt: str = Field(max_length=5000)  # Custom system prompt for this soul
    is_active: bool = Field(default=True)


class AISoulEntity(AISoulEntityBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime | None = Field(default=None)
    interaction_count: int = Field(default=0)

    user: User | None = Relationship(back_populates="ai_souls")
    chat_messages: list["ChatMessage"] = Relationship(back_populates="ai_soul", cascade_delete=True)
    training_messages: list["TrainingMessage"] = Relationship(back_populates="ai_soul", cascade_delete=True)
    training_documents: list["TrainingDocument"] = Relationship(back_populates="ai_soul", cascade_delete=True)
    user_interactions: list["UserAISoulInteraction"] = Relationship(back_populates="ai_soul", cascade_delete=True)


class AISoulEntityCreate(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    persona_type: str = Field(max_length=50)
    specializations: str = Field(max_length=500)
    base_prompt: str | None = Field(default=None, max_length=5000)


class AISoulEntityUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    persona_type: str | None = None
    specializations: str | None = None
    base_prompt: str | None = None
    is_active: bool | None = None


class AISoulEntityPublic(AISoulEntityBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_used: datetime | None
    interaction_count: int


class AISoulEntityWithUserInteraction(AISoulEntityBase):
    """AI Soul Entity with user-specific interaction count for role-based responses"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_used: datetime | None
    interaction_count: int  # This will be either global or user-specific based on role


# Training Message models for AI Soul training
class TrainingMessageBase(SQLModel):
    content: str = Field(min_length=1, max_length=5000)
    is_from_trainer: bool = Field(default=True)  # True if from the person training the AI soul


class TrainingMessage(TrainingMessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding: str | None = Field(default=None, max_length=50000)  # JSON string of embedding vector

    ai_soul: AISoulEntity | None = Relationship()
    user: User | None = Relationship()


class TrainingMessageCreate(TrainingMessageBase):
    pass


class TrainingMessagePublic(TrainingMessageBase):
    id: uuid.UUID
    ai_soul_id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime


# Training Document models for AI Soul training
class TrainingDocumentBase(SQLModel):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_size: int
    content_type: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)


class TrainingDocument(TrainingDocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    file_path: str = Field(max_length=500)
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: str = Field(default="pending", max_length=50)
    chunk_count: int = Field(default=0)

    ai_soul: AISoulEntity | None = Relationship()
    user: User | None = Relationship()


class TrainingDocumentCreate(TrainingDocumentBase):
    pass


class TrainingDocumentPublic(TrainingDocumentBase):
    id: uuid.UUID
    ai_soul_id: uuid.UUID
    user_id: uuid.UUID
    upload_timestamp: datetime
    processing_status: str
    chunk_count: int


# Training Document chunks for AI Soul training
class TrainingDocumentChunk(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    training_document_id: uuid.UUID = Field(
        foreign_key="trainingdocument.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    content: str = Field(min_length=1, max_length=10000)  # Increased from 2000 to 10000
    chunk_index: int
    chunk_metadata: str | None = Field(default=None, max_length=5000)  # Increased from 1000 to 5000
    embedding: str | None = Field(default=None, max_length=50000)  # JSON string of embedding vector
    created_at: datetime = Field(default_factory=datetime.utcnow)

    training_document: TrainingDocument | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    user: User | None = Relationship()


# Enhanced RAG System Models for better search and analytics

# Search Query Analytics
class SearchQueryBase(SQLModel):
    query_text: str = Field(max_length=1000)
    ai_soul_id: uuid.UUID | None = Field(default=None, foreign_key="aisoulentity.id")
    filters_applied: str | None = Field(default=None, max_length=2000)  # JSON string
    results_count: int = Field(default=0)
    response_time_ms: int = Field(default=0)
    user_clicked_result: bool = Field(default=False)
    relevance_feedback: float | None = Field(default=None)  # User feedback score 1-5


class SearchQuery(SearchQueryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()


class SearchQueryPublic(SearchQueryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


# Enhanced Document Chunk with semantic metadata
class DocumentChunkEnhanced(SQLModel, table=True):
    __tablename__ = "document_chunk_enhanced"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # Content and indexing
    content: str = Field(min_length=1, max_length=4000)  # Increased from 2000
    chunk_index: int

    # Semantic metadata (JSON fields for flexibility)
    chunk_metadata: str | None = Field(default=None, max_length=5000)  # Increased from 1000
    semantic_metadata: str | None = Field(default=None, max_length=3000)  # New field

    # Embedding and search data
    embedding_model: str = Field(default="text-embedding-3-small", max_length=100)
    embedding_dimension: int = Field(default=1536)

    # Performance tracking
    search_count: int = Field(default=0)  # How many times this chunk was returned
    click_count: int = Field(default=0)   # How many times user clicked on this chunk
    relevance_score: float | None = Field(default=None)  # Average user feedback

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime | None = Field(default=None)

    # Relationships
    document: Document | None = Relationship()
    user: User | None = Relationship()


# Document processing analytics
class DocumentProcessingLog(SQLModel, table=True):
    __tablename__ = "document_processing_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # Processing details
    processing_stage: str = Field(max_length=50)  # "text_extraction", "chunking", "embedding", "indexing"
    status: str = Field(max_length=20)  # "started", "completed", "failed"
    processing_time_ms: int | None = Field(default=None)

    # Metrics
    chunks_created: int | None = Field(default=None)
    total_tokens: int | None = Field(default=None)
    embedding_cost: float | None = Field(default=None)

    # Error handling
    error_message: str | None = Field(default=None, max_length=2000)
    retry_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)

    # Relationships
    document: Document | None = Relationship()
    user: User | None = Relationship()


# Search result click tracking
class SearchResultClick(SQLModel, table=True):
    __tablename__ = "search_result_click"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    search_query_id: uuid.UUID = Field(
        foreign_key="searchquery.id", nullable=False, ondelete="CASCADE"
    )
    chunk_id: uuid.UUID = Field(
        foreign_key="document_chunk_enhanced.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # Click details
    result_position: int  # Position in search results (1-based)
    similarity_score: float  # Cosine similarity score
    rerank_score: float | None = Field(default=None)  # Cross-encoder score

    # User engagement
    time_spent_ms: int | None = Field(default=None)  # Time spent viewing the result
    user_rating: int | None = Field(default=None)  # 1-5 star rating

    # Timestamps
    clicked_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    search_query: SearchQuery | None = Relationship()
    chunk: DocumentChunkEnhanced | None = Relationship()
    user: User | None = Relationship()


# Enhanced Training Document Chunks (similar enhancements for training data)
class TrainingDocumentChunkEnhanced(SQLModel, table=True):
    __tablename__ = "training_document_chunk_enhanced"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    training_document_id: uuid.UUID = Field(
        foreign_key="trainingdocument.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # Content and indexing
    content: str = Field(min_length=1, max_length=4000)
    chunk_index: int

    # Enhanced metadata
    chunk_metadata: str | None = Field(default=None, max_length=5000)
    semantic_metadata: str | None = Field(default=None, max_length=3000)

    # Embedding info
    embedding_model: str = Field(default="text-embedding-3-small", max_length=100)
    embedding_dimension: int = Field(default=1536)

    # Training-specific fields
    training_importance: float | None = Field(default=None)  # How important for training
    usage_count: int = Field(default=0)  # How many times used in training

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime | None = Field(default=None)

    # Relationships
    training_document: TrainingDocument | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    user: User | None = Relationship()


# RAG System Configuration
class RAGConfiguration(SQLModel, table=True):
    __tablename__ = "rag_configuration"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID | None = Field(
        default=None, foreign_key="aisoulentity.id", ondelete="CASCADE"
    )

    # Configuration settings (JSON)
    chunking_strategy: str = Field(default="semantic", max_length=50)
    chunk_size: int = Field(default=500)
    chunk_overlap: int = Field(default=50)
    embedding_model: str = Field(default="text-embedding-3-small", max_length=100)

    # Search settings
    search_algorithm: str = Field(default="hybrid", max_length=50)
    similarity_threshold: float = Field(default=0.7)
    max_results: int = Field(default=10)
    enable_reranking: bool = Field(default=True)

    # Advanced settings (JSON string)
    advanced_settings: str | None = Field(default=None, max_length=5000)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()


# =============================================================================
# COUNSELOR OVERRIDE & MONITORING SYSTEM MODELS
# =============================================================================

# Organization/Tenant models for multi-tenant support
class OrganizationBase(SQLModel):
    name: str = Field(max_length=255)
    domain: str = Field(max_length=255, unique=True)  # e.g., "church-name.com"
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = Field(default=True)
    max_users: int = Field(default=100)  # Subscription limits
    max_ai_souls: int = Field(default=10)
    settings: str | None = Field(default=None, max_length=5000)  # JSON configuration


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    users: list["User"] = Relationship(back_populates="organization")
    counselors: list["Counselor"] = Relationship(back_populates="organization")


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Enhanced User model with organization and role support
# Note: We'll extend the existing User model in a migration
class UserRole(str, Enum):
    USER = "user"
    TRAINER = "trainer"
    COUNSELOR = "counselor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Counselor model for specialized counselor users
class CounselorBase(SQLModel):
    specializations: str = Field(max_length=500)  # Comma-separated specialties
    license_number: str | None = Field(default=None, max_length=100)
    license_type: str | None = Field(default=None, max_length=100)
    is_available: bool = Field(default=True)
    max_concurrent_cases: int = Field(default=10)
    notification_preferences: str | None = Field(default=None, max_length=2000)  # JSON


class Counselor(CounselorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User | None = Relationship()
    organization: Organization | None = Relationship(back_populates="counselors")
    pending_responses: list["PendingResponse"] = Relationship(back_populates="assigned_counselor")


class CounselorPublic(CounselorBase):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Risk Assessment model for AI conversations
class RiskAssessmentBase(SQLModel):
    risk_level: str = Field(max_length=20)  # "low", "medium", "high", "critical"
    risk_categories: str = Field(max_length=500)  # JSON array of risk types
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str | None = Field(default=None, max_length=2000)
    requires_human_review: bool = Field(default=False)
    auto_response_blocked: bool = Field(default=False)


class RiskAssessment(RiskAssessmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chat_message_id: uuid.UUID = Field(
        foreign_key="chatmessage.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    chat_message: ChatMessage | None = Relationship()
    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    organization: Organization | None = Relationship()


class RiskAssessmentPublic(RiskAssessmentBase):
    id: uuid.UUID
    chat_message_id: uuid.UUID
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    organization_id: uuid.UUID | None
    assessed_at: datetime


# Pending Response model for counselor review queue
class PendingResponseBase(SQLModel):
    original_user_message: str = Field(max_length=5000)
    ai_generated_response: str = Field(max_length=5000)
    status: str = Field(default="pending", max_length=20)  # "pending", "approved", "modified", "rejected"
    priority: str = Field(default="normal", max_length=20)  # "low", "normal", "high", "urgent"
    counselor_notes: str | None = Field(default=None, max_length=2000)
    modified_response: str | None = Field(default=None, max_length=5000)
    response_time_limit: datetime | None = Field(default=None)  # Auto-approve after this time


class PendingResponse(PendingResponseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chat_message_id: uuid.UUID = Field(
        foreign_key="chatmessage.id", nullable=False, ondelete="CASCADE"
    )
    risk_assessment_id: uuid.UUID = Field(
        foreign_key="riskassessment.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    assigned_counselor_id: uuid.UUID | None = Field(
        default=None, foreign_key="counselor.id", ondelete="SET NULL"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: datetime | None = Field(default=None)
    
    # Relationships
    chat_message: ChatMessage | None = Relationship()
    risk_assessment: RiskAssessment | None = Relationship()
    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    assigned_counselor: Counselor | None = Relationship(back_populates="pending_responses")
    organization: Organization | None = Relationship()


class PendingResponsePublic(PendingResponseBase):
    id: uuid.UUID
    chat_message_id: uuid.UUID
    risk_assessment_id: uuid.UUID
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    assigned_counselor_id: uuid.UUID | None
    organization_id: uuid.UUID | None
    created_at: datetime
    reviewed_at: datetime | None


# Counselor Action Log for audit trail
class CounselorActionBase(SQLModel):
    action_type: str = Field(max_length=50)  # "approved", "modified", "rejected", "escalated"
    original_response: str | None = Field(default=None, max_length=5000)
    final_response: str | None = Field(default=None, max_length=5000)
    reason: str | None = Field(default=None, max_length=1000)
    time_taken_seconds: int | None = Field(default=None)


class CounselorAction(CounselorActionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    counselor_id: uuid.UUID = Field(
        foreign_key="counselor.id", nullable=False, ondelete="CASCADE"
    )
    pending_response_id: uuid.UUID = Field(
        foreign_key="pendingresponse.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    counselor: Counselor | None = Relationship()
    pending_response: PendingResponse | None = Relationship()
    user: User | None = Relationship()
    organization: Organization | None = Relationship()


class CounselorActionPublic(CounselorActionBase):
    id: uuid.UUID
    counselor_id: uuid.UUID
    pending_response_id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID | None
    created_at: datetime


# =============================================================================
# ANALYTICS SYSTEM MODELS
# =============================================================================

# Conversation Analytics for tracking usage patterns
class ConversationAnalyticsBase(SQLModel):
    conversation_duration_seconds: int | None = Field(default=None)
    message_count: int = Field(default=0)
    ai_response_count: int = Field(default=0)
    risk_assessments_triggered: int = Field(default=0)
    counselor_interventions: int = Field(default=0)
    user_satisfaction_score: float | None = Field(default=None, ge=1.0, le=5.0)
    topic_categories: str | None = Field(default=None, max_length=1000)  # JSON array


class ConversationAnalytics(ConversationAnalyticsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    session_start: datetime = Field(default_factory=datetime.utcnow)
    session_end: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    organization: Organization | None = Relationship()


class ConversationAnalyticsPublic(ConversationAnalyticsBase):
    id: uuid.UUID
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    organization_id: uuid.UUID | None
    session_start: datetime
    session_end: datetime | None
    created_at: datetime


# Daily Usage Metrics for dashboard analytics
class DailyUsageMetricsBase(SQLModel):
    date: datetime = Field(index=True)
    total_conversations: int = Field(default=0)
    total_messages: int = Field(default=0)
    unique_users: int = Field(default=0)
    ai_responses_generated: int = Field(default=0)
    counselor_interventions: int = Field(default=0)
    high_risk_conversations: int = Field(default=0)
    average_response_time_ms: float | None = Field(default=None)
    user_satisfaction_average: float | None = Field(default=None)


class DailyUsageMetrics(DailyUsageMetricsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Organization | None = Relationship()


class DailyUsageMetricsPublic(DailyUsageMetricsBase):
    id: uuid.UUID
    organization_id: uuid.UUID | None
    created_at: datetime


# Counselor Performance Metrics
class CounselorPerformanceBase(SQLModel):
    date: datetime = Field(index=True)
    cases_reviewed: int = Field(default=0)
    average_review_time_seconds: float | None = Field(default=None)
    approvals: int = Field(default=0)
    modifications: int = Field(default=0)
    rejections: int = Field(default=0)
    escalations: int = Field(default=0)
    user_feedback_score: float | None = Field(default=None, ge=1.0, le=5.0)


class CounselorPerformance(CounselorPerformanceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    counselor_id: uuid.UUID = Field(
        foreign_key="counselor.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    counselor: Counselor | None = Relationship()
    organization: Organization | None = Relationship()


class CounselorPerformancePublic(CounselorPerformanceBase):
    id: uuid.UUID
    counselor_id: uuid.UUID
    organization_id: uuid.UUID | None
    created_at: datetime


# Content Filter Analytics for tracking blocked content
class ContentFilterAnalyticsBase(SQLModel):
    filter_type: str = Field(max_length=50)  # "profanity", "violence", "self_harm", etc.
    content_sample: str | None = Field(default=None, max_length=500)  # Anonymized sample
    severity_level: str = Field(max_length=20)  # "low", "medium", "high"
    action_taken: str = Field(max_length=50)  # "blocked", "warned", "flagged"
    false_positive: bool | None = Field(default=None)  # Manual review result


class ContentFilterAnalytics(ContentFilterAnalyticsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", ondelete="CASCADE"
    )
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship()
    organization: Organization | None = Relationship()


class ContentFilterAnalyticsPublic(ContentFilterAnalyticsBase):
    id: uuid.UUID
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    organization_id: uuid.UUID | None
    detected_at: datetime


# User-specific interaction tracking
class UserAISoulInteractionBase(SQLModel):
    interaction_count: int = Field(default=0)
    last_interaction: datetime | None = Field(default=None)


class UserAISoulInteraction(UserAISoulInteractionBase, table=True):
    __tablename__ = "user_ai_soul_interaction"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    ai_soul_id: uuid.UUID = Field(
        foreign_key="aisoulentity.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship()
    ai_soul: AISoulEntity | None = Relationship(back_populates="user_interactions")

    __table_args__ = (
        UniqueConstraint("user_id", "ai_soul_id", name="unique_user_ai_soul"),
    )


class UserAISoulInteractionPublic(UserAISoulInteractionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    ai_soul_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
