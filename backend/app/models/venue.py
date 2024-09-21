from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

# if TYPE_CHECKING:
#     from .user import UserBusiness
print("Venue models imported")

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

class NightclubUserBusinessLink(SQLModel, table=True):
    nightclub_id: int = Field(foreign_key="nightclub.id", primary_key=True)
    user_business_id: int = Field(foreign_key="user_business.id", primary_key=True)

class Nightclub(VenueBase, table=True):
    __tablename__ = "nightclub"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    # Relationships
    events: List["Event"] = Relationship(back_populates="nightclub")
    club_visits: List["ClubVisit"] = Relationship(back_populates="nightclub")
    menu: List["NightclubMenu"] = Relationship(back_populates="nightclub")
    orders: List["NightclubOrder"] = Relationship(back_populates="nightclub")
    pickup_locations: List["PickupLocation"] = Relationship(back_populates="nightclub")
    group : List["Group"] = Relationship(back_populates="nightclubs")
    managing_users: List["UserBusiness"] = Relationship(
        back_populates="managed_nightclubs",
        link_model=NightclubUserBusinessLink
    )

class RestaurantUserBusinessLink(SQLModel, table=True):
    restaurant_id: int = Field(foreign_key="restaurant.id", primary_key=True)
    user_business_id: int = Field(foreign_key="user_business.id", primary_key=True)

class Restaurant(VenueBase, table=True):
    __tablename__ = "restaurant"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    # Relationships
    menu: List["RestaurantMenu"] = Relationship(back_populates="restaurant")
    orders: List["RestaurantOrder"] = Relationship(back_populates="restaurant")
    managing_users: List["UserBusiness"] = Relationship(
        back_populates="managed_restaurants",
        link_model=RestaurantUserBusinessLink
    )

class QSRUserBusinessLink(SQLModel, table=True):
    qsr_id: int = Field(foreign_key="qsr.id", primary_key=True)
    user_business_id: int = Field(foreign_key="user_business.id", primary_key=True)

class QSR(VenueBase, table=True):
    __tablename__ = "qsr"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    foodcourt_id: Optional[int] = Field(default=None, foreign_key="foodcourt.id")
    # Relationships
    foodcourt: Optional["Foodcourt"] = Relationship(back_populates="qsrs")
    menu: List["QSRMenu"] = Relationship(back_populates="qsr")
    orders: List["QSROrder"] = Relationship(back_populates="qsr")
    managing_users: List["UserBusiness"] = Relationship(
        back_populates="managed_qsrs",
        link_model=QSRUserBusinessLink
    )

class FoodcourtUserBusinessLink(SQLModel, table=True):
    foodcourt_id: int = Field(foreign_key="foodcourt.id", primary_key=True)
    user_business_id: int = Field(foreign_key="user_business.id", primary_key=True)

class Foodcourt(VenueBase, table=True):
    __tablename__ = "foodcourt"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    # Relationships
    qsrs: List["QSR"] = Relationship(back_populates="foodcourt")
    managing_users: List["UserBusiness"] = Relationship(
        back_populates="managed_foodcourts",
        link_model=FoodcourtUserBusinessLink
    )