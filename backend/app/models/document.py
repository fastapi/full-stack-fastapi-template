import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

# --- Retention Policy ---

class RetentionPolicyBase(SQLModel):
    name: str = Field(index=True)
    duration_days: int
    action: str = Field(default="archive") # archive, delete

class RetentionPolicy(RetentionPolicyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
class RetentionPolicyCreate(RetentionPolicyBase):
    pass

class RetentionPolicyUpdate(SQLModel):
    name: str | None = None
    duration_days: int | None = None
    action: str | None = None

class RetentionPolicyRead(RetentionPolicyBase):
    id: uuid.UUID

# --- Document ---

class DocumentBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None
    retention_policy_id: uuid.UUID | None = Field(default=None, foreign_key="retentionpolicy.id")

class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="Draft", index=True)
    current_workflow_id: uuid.UUID | None = Field(default=None, foreign_key="documentworkflowinstance.id")
    
    # Relationships
    versions: list["DocumentVersion"] = Relationship(back_populates="document")
    retention_policy: RetentionPolicy | None = Relationship()
    
    # New relationships for Phase 2
    lock: "DocumentLock" = Relationship(sa_relationship_kwargs={"uselist": False})
    workflow_instances: list["DocumentWorkflowInstance"] = Relationship()

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    retention_policy_id: uuid.UUID | None = None
    status: str | None = None # Draft, In Review, Approved, etc.

class DocumentRead(DocumentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str = "Draft"
    current_workflow_id: uuid.UUID | None = None

# --- Document Version ---

class DocumentVersionBase(SQLModel):
    version_number: int
    file_path: str

class DocumentVersion(DocumentVersionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(foreign_key="document.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: uuid.UUID = Field(foreign_key="user.id")
    
    document: Document = Relationship(back_populates="versions")

class DocumentVersionCreate(DocumentVersionBase):
    pass

class DocumentVersionRead(DocumentVersionBase):
    id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime
    created_by_id: uuid.UUID
