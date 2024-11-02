import uuid
from datetime import time

from pydantic import BaseModel


# Venue base details (composition)
class VenueCreate(BaseModel):
    name: str
    capacity: int | None = None
    description: str | None = None
    instagram_handle: str | None = None
    instagram_token: str | None = None
    mobile_number: str | None = None
    email: str | None = None
    opening_time: time | None = None
    closing_time: time | None = None
    avg_expense_for_two: float | None = None
    zomato_link: str | None = None
    swiggy_link: str | None = None
    google_map_link: str | None = None


class FoodcourtCreate(BaseModel):
    total_qsrs: int | None = None
    seating_capacity: int | None = None
    venue: VenueCreate

    class Config:
        from_attributes = True


class QSRCreate(BaseModel):
    drive_thru: bool | None = False
    foodcourt_id: uuid.UUID | None = None
    venue: VenueCreate

    class Config:
        from_attributes = True


# Restaurant Schemas
class RestaurantCreate(BaseModel):
    cuisine_type: str | None = None
    venue_id: uuid.UUID
    venue: VenueCreate

    class Config:
        from_attributes = True


# Nightclub Schemas
class NightclubCreate(BaseModel):
    venue: VenueCreate
    age_limit: int | None = None

    class Config:
        from_attributes = True


class VenueRead(BaseModel):
    id: uuid.UUID
    name: str
    address: str | None
    latitude: float
    longitude: float
    capacity: int | None
    description: str | None
    google_rating: float | None
    instagram_handle: str | None
    google_map_link: str | None
    mobile_number: str | None
    email: str | None
    opening_time: time | None
    closing_time: time | None
    avg_expense_for_two: float | None
    zomato_link: str | None
    swiggy_link: str | None


class FoodcourtRead(BaseModel):
    id: uuid.UUID
    total_qsrs: int | None = None  # Specific field for foodcourt
    seating_capacity: int | None = None  # Specific to foodcourts
    venue: VenueRead
    qsrs: list["QSRRead"] = []  # list of QSRs in the foodcourt

    class Config:
        from_attributes = True


class QSRRead(BaseModel):
    id: uuid.UUID
    # Add any specific fields for QSR if needed
    foodcourt_id: uuid.UUID | None = None  # Reference to the associated foodcourt
    venue: VenueRead

    class Config:
        from_attributes = True


class RestaurantRead(BaseModel):
    id: uuid.UUID
    cuisine_type: str | None = None
    venue: VenueRead

    class Config:
        from_attributes = True


class NightclubRead(BaseModel):
    id: uuid.UUID
    age_limit: int | None = None
    venue: VenueRead

    class Config:
        from_attributes = True


class VenueListResponse(BaseModel):
    nightclubs: list[NightclubRead]
    qsrs: list[QSRRead]
    foodcourts: list[FoodcourtRead]
    restaurants: list[RestaurantRead]
