from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class QRCodeBase(BaseModel):
    table_number: Optional[str] = Field(default=None, nullable=True)
    foodcourt_id: Optional[UUID] = Field(default=None)
    qsr_id: Optional[UUID] = Field(default=None)
    nightclub_id: Optional[UUID] = Field(default=None)
    restaurant_id: Optional[UUID] = Field(default=None)

class QRCodeCreate(QRCodeBase):
    """
    Schema for creating a new QR code.
    Only one of foodcourt_id, qsr_id, nightclub_id, or restaurant_id should be present.
    """
    
    class Config:
        from_attributes = True

class QRCodeRead(QRCodeBase):
    id: UUID  # Automatically added by the model

    class Config:
        from_attributes = True