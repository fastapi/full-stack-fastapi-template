from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class LookupJobTitles(SQLModel, table=True):
    __tablename__:str='lookup_jobtitles'
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    jobtitle: str = Field()

class LookupJobType(SQLModel, table=True):
    __tablename__:str='lookup_jobtype'
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    jobtype: str = Field()

