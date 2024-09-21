from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)
    title: str = Field(nullable=False)
    start_time: datetime = Field(nullable=False)
    end_time: datetime = Field(nullable=False)
    image_url: Optional[str] = Field(nullable=True)
    age_restriction: Optional[int] = Field(nullable=True)
    dress_code: Optional[str] = Field(nullable=True)

    # Relationships
    nightclub: Optional["Nightclub"] = Relationship(back_populates="events")
    offerings: List["EventOffering"] = Relationship(back_populates="event")
    event_bookings: List["EventBooking"] = Relationship(back_populates="event")