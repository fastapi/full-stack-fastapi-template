import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.venue import Venue
from sqlmodel import Field, Relationship

from app.models.base_model import BaseTimeModel
from app.schema.qrcode import QRCodeCreate, QRCodeRead


class QRCode(BaseTimeModel, table=True):
    __tablename__ = "qrcode"

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    venue_id: uuid.UUID | None = Field(default=None, foreign_key="venue.id")
    table_number: str | None = Field(default=None, nullable=True)

    # Relationships
    venue: Optional["Venue"] = Relationship(back_populates="qrcode")

    @classmethod
    def from_create_schema(cls, schema: "QRCodeCreate") -> "QRCode":
        return cls(venue_id=schema.venue_id, table_number=schema.table_number)

    def to_read_schema(self) -> "QRCodeRead":
        return QRCodeRead(
            id=self.id,  # Access the actual value of the id
            venue_id=self.venue_id,  # Access the actual value of venue_id
            table_number=self.table_number,  # Provide a default empty string if None
        )
