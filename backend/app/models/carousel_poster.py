import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class CarouselPosterBase(SQLModel):
    image_url: str = Field(nullable=False)
    deep_link: str = Field(nullable=False)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    expires_at: datetime = Field(nullable=False)
    
    # Foreign keys [Optional]
    event_id: Optional[uuid.UUID] = Field(default=None, foreign_key="event.id")
    nightclub_id: Optional[uuid.UUID] = Field(default=None, foreign_key="nightclub.id")
    foodcourt_id: Optional[uuid.UUID] = Field(default=None, foreign_key="foodcourt.id")
    qsr_id: Optional[uuid.UUID] = Field(default=None, foreign_key="qsr.id")
    restaurant_id: Optional[uuid.UUID] = Field(default=None, foreign_key="restaurant.id")

class CarouselPoster(CarouselPosterBase, table=True):
    __tablename__ = "carousel_poster"    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    h3_index: str = Field(nullable=False)

    # Relationships [Optional]
    event: Optional["Event"] = Relationship(back_populates="carousel_posters")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="carousel_posters")
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="carousel_posters")
    qsr: Optional["QSR"] = Relationship(back_populates="carousel_posters")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="carousel_posters")