import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class DocumentWorkflowInstance(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(foreign_key="document.id")
    workflow_id: uuid.UUID = Field(foreign_key="workflow.id")
    current_step_id: uuid.UUID | None = Field(default=None, foreign_key="workflowstep.id")
    status: str = Field(default="in_progress") # in_progress, approved, rejected, cancelled
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    
    # Relationships
    # document: "Document" = Relationship()
    # workflow: "Workflow" = Relationship()
    # current_step: "WorkflowStep" = Relationship()
    actions: list["WorkflowAction"] = Relationship(back_populates="workflow_instance")

class WorkflowAction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_instance_id: uuid.UUID = Field(foreign_key="documentworkflowinstance.id")
    step_id: uuid.UUID = Field(foreign_key="workflowstep.id")
    actor_id: uuid.UUID = Field(foreign_key="user.id")
    action: str # approve, reject
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    comments: str | None = None
    
    workflow_instance: DocumentWorkflowInstance = Relationship(back_populates="actions")
