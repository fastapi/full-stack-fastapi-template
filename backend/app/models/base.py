from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel, text

class BaseDBModel(SQLModel):
    """Base model for all database models."""
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            
            index=True,
        ),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            
        ),
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
        orm_mode = True
        
    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Convert model to dictionary, excluding unset fields by default."""
        kwargs.setdefault("exclude_unset", True)
        return super().dict(*args, **kwargs)


class TimestampMixin(SQLModel):
    """
    Mixin to add created_at and updated_at timestamp fields to models.
    These fields will be automatically managed by the database.
    """
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            
        ),
    )
