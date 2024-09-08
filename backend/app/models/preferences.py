from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSON
from typing import List


class JobPreferences(SQLModel, table=True):
    __tablename__:str='pref_jobs'
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    location: str | None = Field(default=None)
    location_coordinates: dict[str, float] | None = Field(sa_column=Column(JSON), default=None)
    remote_bool: bool = Field(default=False)
    h1b_bool: bool = Field(default=False)
    onboarding_id: UUID = Field(foreign_key="user_onboarding.id")
    job_title_preferences: List["JobTitlePreference"] = Relationship(back_populates="job_preferences")
    job_type_preferences: List["JobTypePreference"] = Relationship(back_populates="job_preferences")


class JobTitlePreference(SQLModel, table=True):
    __tablename__:str = 'pref_jobtitle'
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    jobtitle_id: UUID = Field(foreign_key='lookup_jobtitles.id')
    pref_jobs_id: UUID = Field(foreign_key='pref_jobs.id')
    job_preferences: JobPreferences = Relationship(back_populates="job_title_preferences")


class JobTypePreference(SQLModel, table=True):
    __tablename__:str = 'pref_jobtype'
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    jobtype_id: UUID = Field(foreign_key='lookup_jobtype.id')
    pref_jobs_id: UUID = Field(foreign_key='pref_jobs.id')
    job_preferences: JobPreferences = Relationship(back_populates="job_type_preferences")

class JobTitlePreferencePayload(SQLModel):
    jobtitle_id: UUID

class JobTypePreferencePayload(SQLModel):
    jobtype_id: UUID