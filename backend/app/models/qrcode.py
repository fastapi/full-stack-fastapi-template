import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import model_validator, ValidationError

class QRBase(SQLModel):
    table_number: Optional[str] = Field(default=None, nullable=True)

class QRCode(QRBase, table=True):
    __tablename__ = "qr_codes"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    venue_id: Optional[uuid.UUID] = Field(default=None, foreign_key="venue.id")
    
    # Relationships
    venue: Optional["Venue"] = Relationship(back_populates="qr_codes")