import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base_model import BaseTimeModel
from app.schema.carousel_poster import CarouselPosterCreate, CarouselPosterRead

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.venue import Venue


class CarouselPoster(BaseTimeModel, table=True):
    __tablename__ = "carousel_poster"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    h3_index: str = Field(nullable=True, index=True)
    image_url: str = Field(nullable=False)
    deep_link: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False)

    # Foreign keys [Optional]
    event_id: uuid.UUID | None = Field(default=None, foreign_key="event.id")
    venue_id: uuid.UUID | None = Field(default=None, foreign_key="venue.id")

    # Relationships [Optional]
    event: Optional["Event"] = Relationship(back_populates="carousel_posters")
    venue: Optional["Venue"] = Relationship(back_populates="carousel_posters")

    @classmethod
    def from_create_schema(cls, carousel_poster_create: CarouselPosterCreate):
        return cls(
            image_url=carousel_poster_create.image_url,
            deep_link=carousel_poster_create.deep_link,
            expires_at=carousel_poster_create.expires_at,
            event_id=carousel_poster_create.event_id,
            venue_id=carousel_poster_create.venue_id,
        )

    def to_read_schema(self) -> CarouselPosterRead:
        return CarouselPosterRead(
            courosel_id=self.id,
            h3_index=self.h3_index,
            image_url=self.image_url,
            deep_link=self.deep_link,
            expires_at=self.expires_at,
            event_id=self.event_id,
            venue_id=self.venue_id,
        )
