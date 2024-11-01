from uuid import UUID

from pydantic import BaseModel


class QRCodeCreate(BaseModel):
    """
    Schema for creating a new QR code.
    """

    table_number: str | None = None
    venue_id: UUID  # Foreign key to the venue


class QRCodeUpdate(BaseModel):
    """
    Schema for creating a new QR code.
    """

    table_number: str | None = None

class QRCodeRead(BaseModel):
    """
    Schema for reading a QR code.
    """

    id: UUID  # Automatically added by the model
    venue_id: UUID
    table_number: str | None

    class Config:
        from_attributes = True
