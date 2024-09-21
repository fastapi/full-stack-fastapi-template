from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ClubVisit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_public.id", nullable=False)
    group_id: Optional[int] = Field(foreign_key="group.id", nullable=True)
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)
    entry_time: datetime = Field(nullable=False)
    exit_time: Optional[datetime] = Field(nullable=True)
    cover_charge: Optional[float] = Field(nullable=True)
    total_bill: Optional[float] = Field(nullable=True)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="club_visits")
    group: Optional["Group"] = Relationship(back_populates="club_visits")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="club_visits")

