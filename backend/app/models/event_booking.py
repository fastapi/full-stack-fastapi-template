import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class EventBooking(SQLModel, table=True):
    __tablename__ = "event_booking"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user_public.id", nullable=False)
    event_id: Optional[uuid.UUID] = Field(foreign_key="event.id", nullable=False)
    booking_time: datetime = Field(nullable=False)
    total_amount: float = Field(nullable=False)
    status: str = Field(nullable=False)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="event_bookings")
    event: Optional["Event"] = Relationship(back_populates="event_bookings")
    payment: Optional["PaymentEvent"] = Relationship(back_populates="event_booking", sa_relationship_kwargs={"uselist": False})
    event_offerings: List["EventOffering"] = Relationship(back_populates="event_booking")