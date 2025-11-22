import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class DocumentLock(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(foreign_key="document.id", unique=True) # One lock per document
    locked_by_id: uuid.UUID = Field(foreign_key="user.id")
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    
    # Relationships
    # document: "Document" = Relationship(back_populates="lock")
    # locked_by: "User" = Relationship()
