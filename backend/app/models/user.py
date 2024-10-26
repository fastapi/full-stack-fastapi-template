from app.models.group import GroupMembers
from app.models.base_model import BaseTimeModel
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid
from pydantic import EmailStr

# Shared properties
class UserBase(BaseTimeModel):
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    refresh_token: str = Field(nullable=True)

class UserPublic(UserBase, table=True):
    __tablename__ = "user_public"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    phone_number: Optional[str] = Field(unique=True, nullable=False,index=True,default=None)
    email: Optional[EmailStr] = Field(default=None)
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
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user_business.id", primary_key=True)
    venue_id: uuid.UUID = Field(foreign_key="venue.id", primary_key=True)
    role: Optional[str] = Field(default=None)  # e.g., 'manager', 'owner'
    
    user: "UserBusiness" = Relationship(back_populates="venues_association")
    venue: "Venue" = Relationship(back_populates="managing_users")

class UserBusiness(UserBase, table=True):
    __tablename__ = "user_business"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    registration_date: datetime = Field(nullable=False)
    email: EmailStr = Field(unique=True, nullable=False, index=True, max_length=255)
    phone_number: Optional[str] = Field(default=None)
    # Relationships
    venues_association: List[UserVenueAssociation] = Relationship(back_populates="user")