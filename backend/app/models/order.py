import uuid
from app.models.group import GroupNightclubOrderLink
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class OrderBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user_public.id")
    pickup_location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="pickup_location.id")
    note: Optional[str] = Field(nullable=True)
    order_time: datetime = Field(nullable=False)
    total_amount: float = Field(nullable=False)
    taxes_and_charges: Optional[float] = Field(default=None)
    cover_charge_used: Optional[float] = Field(default=None)
    status: str = Field(nullable=False)
    service_type: Optional[str] = Field(default=None)

class NightclubOrder(OrderBase, table=True):
    __tablename__ = "nightclub_order"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: Optional[uuid.UUID] = Field(default=None, foreign_key="nightclub.id")
    payment_id: Optional[uuid.UUID] = Field(default=None, foreign_key="payment_source_nightclub.id")
    pickup_location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="pickup_location.id")
    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="nightclub_orders")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="orders")
    pickup_location: Optional["PickupLocation"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderNightclub"] = Relationship(back_populates="order", sa_relationship_kwargs={"uselist": False})
    groups: List["Group"] = Relationship(back_populates="nightclub_orders", link_model=GroupNightclubOrderLink)  # Many-to-many
    order_items: List["OrderItem"] = Relationship(back_populates="nightclub_order")

class RestaurantOrder(OrderBase, table=True):
    __tablename__ = "restaurant_order"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: Optional[uuid.UUID] = Field(default=None, foreign_key="restaurant.id")
    payment_id: Optional[uuid.UUID] = Field(default=None, foreign_key="payment_source_restaurant.id")

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="restaurant_orders")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderRestaurant"] = Relationship(back_populates="order", sa_relationship_kwargs={"uselist": False})
    order_items: List["OrderItem"] = Relationship(back_populates="restaurant_order")

class QSROrder(OrderBase, table=True):
    __tablename__ = "qsr_order"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(default=None, foreign_key="qsr.id")
    payment_id: uuid.UUID = Field(default=None, foreign_key="payment_source_qsr.id")

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="qsr_orders")
    qsr: Optional["QSR"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderQSR"] = Relationship(back_populates="order", sa_relationship_kwargs={"uselist": False})
    order_items: List["OrderItem"] = Relationship(back_populates="qsr_order")