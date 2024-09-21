from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class EventBooking(SQLModel, table=True):
    __tablename__ = "event_booking"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_public.id", nullable=False)
    event_id: int = Field(foreign_key="event.id", nullable=False)
    booking_time: datetime = Field(nullable=False)
    total_amount: float = Field(nullable=False)
    status: str = Field(nullable=False)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="event_bookings")
    event: Optional["Event"] = Relationship(back_populates="event_bookings")
    payment: Optional["PaymentEvent"] = Relationship(back_populates="event_booking", sa_relationship_kwargs={"uselist": False})
    event_offerings: List["EventOffering"] = Relationship(back_populates="event_booking")