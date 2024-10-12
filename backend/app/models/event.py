import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Event(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    nightclub_id: uuid.UUID  = Field(foreign_key="nightclub.id", nullable=False)
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
    carousel_posters: Optional[List["CarouselPoster"]] = Relationship(back_populates="event")