from app.models.group import GroupMembers
from app.models.base_model import BaseTimeModel
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid
from pydantic import EmailStr

# Shared properties
class UserBase(BaseTimeModel):
    email: EmailStr = Field(unique=True, nullable=True, index=True, max_length=255)
    phone_number: Optional[str] = Field(unique=True, nullable=False,index=True,default=None)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    refresh_token: str = Field(nullable=True)

class UserPublic(UserBase, table=True):
    __tablename__ = "user_public"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    date_of_birth: Optional[datetime] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    registration_date: datetime = Field(nullable=False)
    profile_picture: Optional[str] = Field(default=None)
    preferences: Optional[str] = Field(default=None)

    # Relationships
    nightclub_orders: List["NightclubOrder"] = Relationship(back_populates="user")
    restaurant_orders: List["RestaurantOrder"] = Relationship(back_populates="user")
    qsr_orders: List["QSROrder"] = Relationship(back_populates="user")
    
    club_visits: List["ClubVisit"] = Relationship(back_populates="user")
    event_bookings: List["EventBooking"] = Relationship(back_populates="user")
    groups: List["Group"] = Relationship(back_populates="members", link_model=GroupMembers)
    managed_groups: List["Group"] = Relationship(back_populates="admin_user")
    nightclub_payments: List["PaymentOrderNightclub"] = Relationship(back_populates="user")
    qsr_payments: List["PaymentOrderQSR"] = Relationship(back_populates="user")
    restaurant_payments: List["PaymentOrderRestaurant"] = Relationship(back_populates="user")
    event_payments: List["PaymentEvent"] = Relationship(back_populates="user")

class UserVenueAssociation(SQLModel, table=True):
    __tablename__ = "user_venue_association"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # Add a primary key
    user_business_id: uuid.UUID = Field(foreign_key="user_business.id")
    venue_id: uuid.UUID = Field(foreign_key="venue.id")

    # Additional fields can be added for tracking roles, timestamps, etc.
    role: Optional[str] = Field(default=None)  # e.g., 'manager', 'owner'

    user_business: "UserBusiness" = Relationship(back_populates="venue_associations")
    venue: "Venue" = Relationship(back_populates="user_associations")
class UserBusiness(UserBase, table=True):
    __tablename__ = "user_business"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    registration_date: datetime = Field(nullable=False)

    # Relationships
    venue_associations: List["UserVenueAssociation"] = Relationship(back_populates="user_business")
    managed_venues: List["Venue"] = Relationship(back_populates="managing_users", link_model=UserVenueAssociation)