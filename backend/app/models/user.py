import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.constants import Gender
from app.models.base_model import BaseTimeModel
from app.models.club_visit import ClubVisit
from app.models.event_booking import EventBooking
from app.models.group import GroupMembers
from app.models.order import NightclubOrder, QSROrder, RestaurantOrder
from app.models.payment import (
    PaymentEvent,
    PaymentOrderNightclub,
    PaymentOrderQSR,
    PaymentOrderRestaurant,
)
from app.models.venue import Venue

if TYPE_CHECKING:
    from app.models.group import Group

from app.schema.user import (
    UserBusinessCreate,
    UserBusinessRead,
    UserPublicCreate,
    UserPublicRead,
)


# Shared properties
class UserBase(BaseTimeModel):
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    refresh_token: str = Field(nullable=True)


class UserPublic(UserBase, table=True):
    __tablename__ = "user_public"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    phone_number: str | None = Field(
        unique=True, nullable=False, index=True, default=None
    )
    email: EmailStr | None = Field(default=None)
    date_of_birth: datetime | None = Field(default=None)
    gender: Gender | None = Field(default=None)
    profile_picture: str | None = Field(default=None)
    preferences: str | None = Field(default=None)

    # Relationships
    nightclub_orders: list["NightclubOrder"] = Relationship(back_populates="user")
    restaurant_orders: list["RestaurantOrder"] = Relationship(back_populates="user")
    qsr_orders: list["QSROrder"] = Relationship(back_populates="user")

    club_visits: list["ClubVisit"] = Relationship(back_populates="user")
    event_bookings: list["EventBooking"] = Relationship(back_populates="user")
    groups: list["Group"] = Relationship(
        back_populates="members", link_model=GroupMembers
    )
    managed_groups: list["Group"] = Relationship(back_populates="admin_user")
    nightclub_payments: list["PaymentOrderNightclub"] = Relationship(
        back_populates="user"
    )
    qsr_payments: list["PaymentOrderQSR"] = Relationship(back_populates="user")
    restaurant_payments: list["PaymentOrderRestaurant"] = Relationship(
        back_populates="user"
    )
    event_payments: list["PaymentEvent"] = Relationship(back_populates="user")

    @classmethod
    def from_create_schema(cls, schema: UserPublicCreate) -> "UserPublic":
        return cls(
            full_name=schema.full_name,
            phone_number=schema.phone_number,
            email=schema.email,
            date_of_birth=schema.date_of_birth,
            gender=schema.gender,
            profile_picture=schema.profile_picture,
            preferences=schema.preferences,
        )

    def to_read_schema(self) -> UserPublicRead:
        return UserPublicRead(
            id=self.id,
            full_name=self.full_name,
            phone_number=self.phone_number,
            email=self.email,
            date_of_birth=self.date_of_birth,
            gender=self.gender,
            profile_picture=self.profile_picture,
            preferences=self.preferences,
        )


class UserVenueAssociation(SQLModel, table=True):
    __tablename__ = "user_venue_association"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user_business.id", primary_key=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", primary_key=True)
    role: str | None = Field(default=None)  # e.g., 'manager', 'owner'

    user: "UserBusiness" = Relationship(back_populates="venues_association")
    venue: "Venue" = Relationship(back_populates="managing_users")


class UserBusiness(UserBase, table=True):
    __tablename__ = "user_business"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: EmailStr = Field(unique=True, nullable=False, index=True, max_length=255)
    phone_number: str | None = Field(default=None)
    # Relationships
    venues_association: list[UserVenueAssociation] = Relationship(back_populates="user")

    @classmethod
    def from_create_schema(cls, schema: UserBusinessCreate) -> "UserBusiness":
        return cls(
            full_name=schema.full_name,
            email=schema.email,
            phone_number=schema.phone_number,
        )

    def to_read_schema(self) -> UserBusinessRead:
        return UserBusinessRead(
            id=self.id,
            full_name=self.full_name,
            email=self.email,
            phone_number=self.phone_number,
        )
