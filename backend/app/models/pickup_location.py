from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class PickupLocation(SQLModel, table=True):
    __tablename__ = "pickup_location"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Relationships
    orders: List["NightclubOrder"] = Relationship(back_populates="pickup_location")

    # Optionally, if you have a specific type of venue for PickupLocation
    nightclub: Optional["Nightclub"] = Relationship(back_populates="pickup_locations")