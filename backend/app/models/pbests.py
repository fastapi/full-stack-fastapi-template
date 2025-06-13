import uuid
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel

# Import directly from user module to avoid circular imports
from app.models.user import User


class PersonalBestBase(SQLModel):
    id: Optional[UUID] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    exercise_name: str
    metric_type: str
    metric_value: float
    date_achieved: date


class PersonalBest(PersonalBestBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    
    # Define the relationship to User (back_populates must match what's in User)
    user: User = Relationship(back_populates="personal_bests")


class PersonalBestCreate(PersonalBestBase):
    pass


class PersonalBestPublic(PersonalBestBase):
    id: UUID
    user_id: UUID


class PersonalBestsList(SQLModel):
    data: list[PersonalBestPublic]
    count: int


class PersonalBestRead(SQLModel):
    id: UUID
    user_id: UUID
    exercise_name: str
    metric_type: str
    metric_value: float
    date_achieved: datetime

