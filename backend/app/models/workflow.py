import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

# --- Workflow ---

class WorkflowBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = None

class Workflow(WorkflowBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    steps: list["WorkflowStep"] = Relationship(back_populates="workflow")

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(SQLModel):
    name: str | None = None
    description: str | None = None

class WorkflowRead(WorkflowBase):
    id: uuid.UUID

# --- Workflow Step ---

class WorkflowStepBase(SQLModel):
    name: str
    order: int
    approver_role: str | None = None

class WorkflowStep(WorkflowStepBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(foreign_key="workflow.id")
    
    workflow: Workflow = Relationship(back_populates="steps")

class WorkflowStepCreate(WorkflowStepBase):
    pass

class WorkflowStepUpdate(SQLModel):
    name: str | None = None
    order: int | None = None
    approver_role: str | None = None

class WorkflowStepRead(WorkflowStepBase):
    id: uuid.UUID
    workflow_id: uuid.UUID

# --- Audit Log ---

class AuditLogBase(SQLModel):
    action: str
    details: str | None = None

class AuditLog(AuditLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID | None = Field(default=None, foreign_key="document.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AuditLogRead(AuditLogBase):
    id: uuid.UUID
    document_id: uuid.UUID | None
    user_id: uuid.UUID
    timestamp: datetime
