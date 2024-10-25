from sqlmodel import SQLModel, Field
from datetime import timezone, datetime
from typing import Optional

class BaseTimeModel(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)