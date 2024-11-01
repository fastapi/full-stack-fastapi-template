import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.group import GroupNightclubOrderLink

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.order_item import OrderItem
    from app.models.payment import (
        PaymentOrderNightclub,
        PaymentOrderQSR,
        PaymentOrderRestaurant,
    )
    from app.models.pickup_location import PickupLocation
    from app.models.user import UserPublic
    from app.models.venue import QSR, Nightclub, Restaurant


class OrderBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user_public.id")
    pickup_location_id: uuid.UUID | None = Field(
        default=None, foreign_key="pickup_location.id"
    )
    note: str | None = Field(nullable=True)
    order_time: datetime = Field(nullable=False)
    total_amount: float = Field(nullable=False)
    taxes_and_charges: float | None = Field(default=None)
    cover_charge_used: float | None = Field(default=None)
    status: str = Field(nullable=False)
    service_type: str | None = Field(default=None)


class NightclubOrder(OrderBase, table=True):
    __tablename__ = "nightclub_order"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID | None = Field(default=None, foreign_key="nightclub.id")
    payment_id: uuid.UUID | None = Field(
        default=None, foreign_key="payment_source_nightclub.id"
    )
    pickup_location_id: uuid.UUID | None = Field(
        default=None, foreign_key="pickup_location.id"
    )
    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="nightclub_orders")
    nightclub: Optional["Nightclub"] = Relationship(back_populates="orders")
    pickup_location: Optional["PickupLocation"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderNightclub"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )
    groups: list["Group"] = Relationship(
        back_populates="nightclub_orders", link_model=GroupNightclubOrderLink
    )  # Many-to-many
    order_items: list["OrderItem"] = Relationship(back_populates="nightclub_order")


class RestaurantOrder(OrderBase, table=True):
    __tablename__ = "restaurant_order"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID | None = Field(default=None, foreign_key="restaurant.id")
    payment_id: uuid.UUID | None = Field(
        default=None, foreign_key="payment_source_restaurant.id"
    )

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="restaurant_orders")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderRestaurant"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )
    order_items: list["OrderItem"] = Relationship(back_populates="restaurant_order")


class QSROrder(OrderBase, table=True):
    __tablename__ = "qsr_order"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    venue_id: uuid.UUID = Field(default=None, foreign_key="qsr.id")
    payment_id: uuid.UUID = Field(default=None, foreign_key="payment_source_qsr.id")

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="qsr_orders")
    qsr: Optional["QSR"] = Relationship(back_populates="orders")
    payment: Optional["PaymentOrderQSR"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )
    order_items: list["OrderItem"] = Relationship(back_populates="qsr_order")
