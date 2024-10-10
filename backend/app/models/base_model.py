from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class BaseTimeModel(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=datetime.now(datetime.timezone.utc), nullable=False)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(datetime.timezone.utc), nullable=False)