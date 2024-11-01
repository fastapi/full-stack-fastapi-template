import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import UserPublic
    from app.models.venue import Nightclub


class ClubVisit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(foreign_key="user_public.id", nullable=False)
    group_id: uuid.UUID | None = Field(foreign_key="group.id", nullable=True)
    nightclub_id: uuid.UUID | None = Field(foreign_key="nightclub.id", nullable=False)
    entry_time: datetime = Field(nullable=False)
    exit_time: datetime | None = Field(nullable=True)
    cover_charge: float | None = Field(nullable=True)
    total_bill: float | None = Field(nullable=True)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="club_visits")
    group: Optional["Group"] = Relationship(back_populates="club_visits")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="club_visits")
