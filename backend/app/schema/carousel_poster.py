from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime
from app.models.carousel_poster import CarouselPosterBase

class CarouselPosterCreate(CarouselPosterBase):
    class Config:
        from_attributes = True

class CarouselPosterRead(CarouselPosterBase):
    id: Optional[uuid.UUID]
    class Config:
        from_attributes = True