import uuid
from datetime import time
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base_model import BaseTimeModel

if TYPE_CHECKING:
    from app.models.carousel_poster import CarouselPoster
    from app.models.club_visit import ClubVisit
    from app.models.event import Event
    from app.models.group import Group
    from app.models.menu import Menu
    from app.models.order import NightclubOrder, QSROrder, RestaurantOrder
    from app.models.pickup_location import PickupLocation
    from app.models.qrcode import QRCode
    from app.models.user import UserVenueAssociation

from app.schema.venue import (
    FoodcourtCreate,
    FoodcourtRead,
    NightclubCreate,
    NightclubRead,
    QSRCreate,
    QSRRead,
    RestaurantCreate,
    RestaurantRead,
    VenueCreate,
    VenueRead,
)


class Venue(BaseTimeModel, table=True):
    __tablename__ = "venue"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )  # Missing id field
    name: str = Field(nullable=False, index=True)
    address: str | None = Field(default=None)
    latitude: float  = Field(default=0)
    longitude: float  = Field(default=0)
    capacity: int | None = Field(default=None)
    description: str | None = Field(default=None)
    google_rating: float | None = Field(default=None)
    instagram_handle: str | None = Field(default=None)
    instagram_token: str | None = Field(default=None)
    google_map_link: str | None = Field(default=None)
    mobile_number: str | None = Field(default=None)
    email: str | None = Field(default=None)
    opening_time: time | None = Field(default=None)
    closing_time: time | None = Field(default=None)
    avg_expense_for_two: float | None = Field(default=None)
    zomato_link: str | None = Field(default=None)
    swiggy_link: str | None = Field(default=None)

    managing_users: list["UserVenueAssociation"] = Relationship(back_populates="venue")
    qrcode: list["QRCode"] = Relationship(back_populates="venue")
    menu: list["Menu"] = Relationship(back_populates="venue")
    pickup_locations: list["PickupLocation"] = Relationship(back_populates="venue")
    carousel_posters: list["CarouselPoster"] | None = Relationship(back_populates="venue")

    # Back-references for specific venue types
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="venue")
    qsr: Optional["QSR"] = Relationship(back_populates="venue")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="venue")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="venue")
    events: list["Event"] = Relationship(back_populates="venue")

    @classmethod
    def from_create_schema(cls, venue_create: VenueCreate) -> "Venue":
        return cls(
            name=venue_create.name,
            capacity=venue_create.capacity,
            description=venue_create.description,
            instagram_handle=venue_create.instagram_handle,
            instagram_token=venue_create.instagram_token,
            google_map_link=venue_create.google_map_link,
            mobile_number=venue_create.mobile_number,
            email=venue_create.email,
            opening_time=venue_create.opening_time,
            closing_time=venue_create.closing_time,
            avg_expense_for_two=venue_create.avg_expense_for_two,
            zomato_link=venue_create.zomato_link,
            swiggy_link=venue_create.swiggy_link,
        )

    def to_read_schema(self) -> VenueRead:
        return VenueRead(
            id=self.id,
            name=self.name,
            address=self.address,
            latitude=self.latitude,
            longitude=self.longitude,
            capacity=self.capacity,
            description=self.description,
            google_rating=self.google_rating,
            instagram_handle=self.instagram_handle,
            google_map_link=self.google_map_link,
            mobile_number=self.mobile_number,
            email=self.email,
            opening_time=self.opening_time,
            closing_time=self.closing_time,
            avg_expense_for_two=self.avg_expense_for_two,
            zomato_link=self.zomato_link,
            swiggy_link=self.swiggy_link,
        )


# Specific Venue Types
class Foodcourt(BaseTimeModel, table=True):
    __tablename__ = "foodcourt"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    total_qsrs: int | None = Field(default=None)  # Example specific field for foodcourt
    seating_capacity: int | None = Field(default=None)  # Specific to foodcourts
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False, index=True)

    # Relationships
    venue: Venue = Relationship(back_populates="foodcourt")
    qsrs: list["QSR"] = Relationship(back_populates="foodcourt")

    @classmethod
    def from_create_schema(
        cls, venue_id: uuid, foodcourt_create: FoodcourtCreate
    ) -> "Foodcourt":
        return cls(
            total_qsrs=foodcourt_create.total_qsrs,
            seating_capacity=foodcourt_create.seating_capacity,
            venue_id=venue_id,
        )

    def to_read_schema(self) -> FoodcourtRead:
        venue_read = self.venue.to_read_schema()
        return FoodcourtRead(
            id=self.id,
            total_qsrs=self.total_qsrs,
            seating_capacity=self.seating_capacity,
            venue=venue_read,
            qsrs=[qsr.to_read_schema() for qsr in self.qsrs],
        )


class QSR(BaseTimeModel, table=True):
    __tablename__ = "qsr"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    foodcourt_id: uuid.UUID | None = Field(
        foreign_key="foodcourt.id", nullable=True, index=True
    )

    drive_thru: bool | None = Field(default=False)  # Specific field for QSR
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False, index=True)

    venue: Venue = Relationship(back_populates="qsr")
    foodcourt: Foodcourt | None = Relationship(back_populates="qsrs")
    orders: list["QSROrder"] = Relationship(back_populates="qsr")

    @classmethod
    def from_create_schema(cls, venue_id: uuid, qsr_create: QSRCreate) -> "QSR":
        return cls(
            foodcourt_id=qsr_create.foodcourt_id,
            drive_thru=qsr_create.drive_thru,
            venue_id=venue_id,
        )

    def to_read_schema(self) -> QSRRead:
        venue_read = self.venue.to_read_schema()
        return QSRRead(
            id=self.id,
            foodcourt_id=self.foodcourt_id,
            drive_thru=self.drive_thru,
            venue=venue_read,
        )


class Restaurant(BaseTimeModel, table=True):
    __tablename__ = "restaurant"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False, index=True)
    venue: Venue = Relationship(back_populates="restaurant")
    cuisine_type: str | None = Field(
        default=None
    )  # Example specific field for restaurant
    orders: list["RestaurantOrder"] = Relationship(back_populates="restaurant")

    @classmethod
    def from_create_schema(
        cls, venue_id, restaurant_create: RestaurantCreate
    ) -> "Restaurant":
        return cls(
            venue_id=venue_id,
            cuisine_type=restaurant_create.cuisine_type,
        )

    def to_read_schema(self) -> RestaurantRead:
        venue_read = self.venue.to_read_schema()
        return RestaurantRead(
            id=self.id,
            venue=venue_read,
            cuisine_type=self.cuisine_type,
        )


class Nightclub(BaseTimeModel, table=True):
    __tablename__ = "nightclub"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False, index=True)
    age_limit: int | None = Field(default=None)
    # Relationships
    club_visits: list["ClubVisit"] = Relationship(back_populates="nightclub")
    orders: list["NightclubOrder"] = Relationship(back_populates="nightclub")
    group: list["Group"] = Relationship(back_populates="nightclubs")
    venue: Venue = Relationship(back_populates="nightclub")

    @classmethod
    def from_create_schema(
        cls, venue_id, nightclub_create: NightclubCreate
    ) -> "Nightclub":
        return cls(
            venue_id=venue_id,
            age_limit=nightclub_create.age_limit,
        )

    def to_read_schema(self) -> NightclubRead:
        venue_read = self.venue.to_read_schema()
        return NightclubRead(
            age_limit=self.age_limit,
            id=self.id,
            venue=venue_read,
        )
