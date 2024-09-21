from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional


# Base model shared by all venues
class VenueBase(SQLModel):
    name: str = Field(nullable=False)
    address: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    capacity: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    google_rating: Optional[float] = Field(default=None)
    instagram_handle: Optional[str] = Field(default=None)
    instagram_token: Optional[str] = Field(default=None)
    google_map_link: Optional[str] = Field(default=None)
    mobile_number: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    opening_time: Optional[str] = Field(default=None)
    closing_time: Optional[str] = Field(default=None)
    avg_expense_for_two: Optional[float] = Field(default=None)
    qr_url: Optional[str] = Field(default=None)


# --------- Nightclub Models ---------
class Nightclub(VenueBase, table=True):
    __tablename__ = "nightclub"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    events: List["Event"] = Relationship(back_populates="nightclub")
    club_visits: List["ClubVisit"] = Relationship(back_populates="nightclub")
    menu: List["NightclubMenu"] = Relationship(back_populates="nightclub")
    orders: List["NightclubOrder"] = Relationship(back_populates="nightclub")
    pickup_locations: List["PickupLocation"] = Relationship(back_populates="nightclub")
    group: List["Group"] = Relationship(back_populates="nightclubs")


# --------- Restaurant Models ---------
class Restaurant(VenueBase, table=True):
    __tablename__ = "restaurant"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    foodcourt_id: Optional[int] = Field(default=None, foreign_key="foodcourt.id")

    # Relationships
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="qsrs")
    menu: List["RestaurantMenu"] = Relationship(back_populates="restaurant")
    orders: List["RestaurantOrder"] = Relationship(back_populates="restaurant")


# --------- QSR Models ---------
class QSR(VenueBase, table=True):
    __tablename__ = "qsr"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    foodcourt_id: Optional[int] = Field(default=None, foreign_key="foodcourt.id")

    # Relationships
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="qsrs")
    menu: List["QSRMenu"] = Relationship(back_populates="qsr")
    orders: List["QSROrder"] = Relationship(back_populates="qsr")


# --------- Foodcourt Models ---------
class Foodcourt(VenueBase, table=True):
    __tablename__ = "foodcourt"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    qsrs: List["QSR"] = Relationship(back_populates="foodcourt")

# --------- PickupLocation Models ---------
class PickupLocation(SQLModel, table=True):
    __tablename__ = "pickup_location"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    venue_id: int = Field(foreign_key="venue.id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Relationships
    orders: List["NightclubOrder"] = Relationship(back_populates="pickup_location")

    # Optionally, if you have a specific type of venue for PickupLocation
    nightclub: Optional["Nightclub"] = Relationship(back_populates="pickup_locations")

# ------------------ SCHEMAS ------------------

# --------- Nightclub Schemas ---------
class NightclubCreate(VenueBase):
    pass


class NightclubRead(VenueBase):
    id: int


class NightclubUpdate(VenueBase):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    google_rating: Optional[float] = None
    instagram_handle: Optional[str] = None
    google_map_link: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    avg_expense_for_two: Optional[float] = None
    qr_url: Optional[str] = None

class NightclubDelete(SQLModel):
    id: int

# --------- Restaurant Schemas ---------
class RestaurantCreate(VenueBase):
    pass


class RestaurantRead(VenueBase):
    id: int


class RestaurantUpdate(VenueBase):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    google_rating: Optional[float] = None
    instagram_handle: Optional[str] = None
    google_map_link: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    avg_expense_for_two: Optional[float] = None
    qr_url: Optional[str] = None

class RestaurantDelete(SQLModel):
    id: int


# --------- QSR Schemas ---------
class QSRCreate(VenueBase):
    pass


class QSRRead(VenueBase):
    id: int


class QSRUpdate(VenueBase):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    google_rating: Optional[float] = None
    instagram_handle: Optional[str] = None
    google_map_link: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    avg_expense_for_two: Optional[float] = None
    qr_url: Optional[str] = None

class QSRDelete(SQLModel):
    id: int

# --------- Foodcourt Schemas ---------
class FoodCourtCreate(VenueBase):
    pass


class FoodCourtRead(VenueBase):
    id: int


class FoodCourtUpdate(VenueBase):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    google_rating: Optional[float] = None
    instagram_handle: Optional[str] = None
    google_map_link: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    avg_expense_for_two: Optional[float] = None
    qr_url: Optional[str] = None


class FoodCourtDelete(SQLModel):
    id: int


# --------- PickupLocation Schemas ---------
class PickupLocationCreate(SQLModel):
    venue_id: int
    name: str
    description: Optional[str] = None


class PickupLocationRead(SQLModel):
    id: int
    venue_id: int
    name: str
    description: Optional[str] = None


class PickupLocationUpdate(SQLModel):
    venue_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


class PickupLocationDelete(SQLModel):
    id: int