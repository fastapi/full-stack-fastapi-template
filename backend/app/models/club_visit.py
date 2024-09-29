import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ClubVisit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user_public.id", nullable=False)
    group_id: Optional[uuid.UUID] = Field(foreign_key="group.id", nullable=True)
    nightclub_id: Optional[uuid.UUID] = Field(foreign_key="nightclub.id", nullable=False)
    entry_time: datetime = Field(nullable=False)
    exit_time: Optional[datetime] = Field(nullable=True)
    cover_charge: Optional[float] = Field(nullable=True)
    total_bill: Optional[float] = Field(nullable=True)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="club_visits")
    group: Optional["Group"] = Relationship(back_populates="club_visits")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="club_visits")

