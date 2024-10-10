import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import model_validator, ValidationError

class QRBase(SQLModel):
    table_number: Optional[str] = Field(default=None, nullable=True)

class QRCode(QRBase, table=True):
    __tablename__ = "qr_codes"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # References
    foodcourt_id: Optional[uuid.UUID] = Field(default=None, foreign_key="foodcourt.id")
    qsr_id: Optional[uuid.UUID] = Field(default=None, foreign_key="qsr.id")
    nightclub_id: Optional[uuid.UUID] = Field(default=None, foreign_key="nightclub.id")
    restaurant_id: Optional[uuid.UUID] = Field(default=None, foreign_key="restaurant.id")

    # Relationships
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="qr_codes")
    qsr: Optional["QSR"] = Relationship(back_populates="qr_codes")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="qr_codes")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="qr_codes")

    # Custom model validator to ensure exactly one foreign key is present
    @model_validator(mode="before")
    def check_one_foreign_key(cls, values):
        foodcourt_id = values.get("foodcourt_id")
        qsr_id = values.get("qsr_id")
        nightclub_id = values.get("nightclub_id")
        restaurant_id = values.get("restaurant_id")

        # Count how many of the foreign key fields are set
        count = sum(v is not None for v in [foodcourt_id, qsr_id, nightclub_id, restaurant_id])
        
        if count != 1:
            raise ValueError("Exactly one of the following must be set: foodcourt_id, qsr_id, nightclub_id, restaurant_id.")
        
        return values
