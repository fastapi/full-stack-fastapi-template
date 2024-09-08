from uuid import UUID, uuid4
from typing import List
from sqlmodel import SQLModel, Relationship, Field
from pydantic import validator
from .preferences import JobTitlePreferencePayload, JobTypePreferencePayload

class UserOnboarding(SQLModel, table=True):
    __tablename__:str = "user_onboarding"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    urgency_level: int = Field(default=1)    

    @validator("urgency_level")
    def validate_urgency_level(cls, v):
        if v and v not in [1,2,3]:
            raise ValueError("Urgency level must be 1, 2 or 3")
        return v


class UserOnBoardingPayload(SQLModel):
    urgency_level: int = 1
    pref_job_title: List[JobTitlePreferencePayload]
    pref_job_type: List[JobTypePreferencePayload]
    location: str
    location_coordinates: dict[str, float]
    remote_bool: bool = False
    h1b_bool: bool = False
