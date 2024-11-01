import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.order import NightclubOrder
    from app.models.venue import Venue
from sqlmodel import Field, Relationship, SQLModel


class PickupLocation(SQLModel, table=True):
    __tablename__ = "pickup_location"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)

    # Relationships
    orders: list["NightclubOrder"] = Relationship(back_populates="pickup_location")

    # Optionally, if you have a specific type of venue for PickupLocation
    venue: Optional["Venue"] = Relationship(back_populates="pickup_locations")
