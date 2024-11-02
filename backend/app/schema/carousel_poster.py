import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator


class CarouselPosterCreate(BaseModel):
    image_url: str
    deep_link: str
    expires_at: datetime
    event_id: uuid.UUID | None = None
    venue_id: uuid.UUID | None = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def validate_event_or_venue(cls, values):
        event_id, venue_id = values.get('event_id'), values.get('venue_id')
        if bool(event_id) == bool(venue_id):  # Both or neither are set
            raise ValueError("Exactly one of 'event_id' or 'venue_id' must be provided.")
        return values

class CarouselPosterRead(BaseModel):
    courosel_id: uuid.UUID
    image_url: str
    deep_link: str
    h3_index: str | None
    expires_at: datetime
    event_id: uuid.UUID | None
    venue_id: uuid.UUID | None

    class Config:
        from_attributes = True
