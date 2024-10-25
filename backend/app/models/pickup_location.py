import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class PickupLocation(SQLModel, table=True):
    __tablename__ = "pickup_location"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Relationships
    orders: List["NightclubOrder"] = Relationship(back_populates="pickup_location")

    # Optionally, if you have a specific type of venue for PickupLocation
    venue: Optional["Venue"] = Relationship(back_populates="pickup_locations")