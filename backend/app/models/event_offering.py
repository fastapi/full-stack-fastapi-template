import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from typing import List

# Stag, couple etc
class EventOffering(SQLModel, table=True):
    __tablename__ = "event_offering"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)
    event_booking_id: uuid.UUID = Field(foreign_key="event_booking.id", nullable=False)
    offering_type: str = Field(nullable=False)
    description: str = Field(nullable=False)
    price: float = Field(nullable=False)
    total_guests_per_pass: int = Field(nullable=False)
    cover_charge: Optional[float] = Field(nullable=True)
    additional_charges: Optional[float] = Field(nullable=True)
    availability: int = Field(nullable=False)

    # Relationships
    event: Optional["Event"] = Relationship(back_populates="offerings")
    event_booking: Optional["EventBooking"] = Relationship(back_populates="event_offerings")