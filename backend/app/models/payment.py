import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.event_booking import EventBooking
    from app.models.order import NightclubOrder, QSROrder, RestaurantOrder
    from app.models.user import UserPublic
from sqlmodel import Field, Relationship, SQLModel


class PaymentBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user_public.id", nullable=False)
    source_type: str = Field(nullable=False)  # Changed to str
    gateway_transaction_id: uuid.UUID | None = Field(default=None)
    payment_time: datetime = Field(nullable=False)
    amount: float = Field(nullable=False)
    status: str = Field(nullable=False)  # e.g., Paid, Pending, Failed
    source_type: str = Field(nullable=False)


class PaymentOrderNightclub(PaymentBase, table=True):
    __tablename__ = "payment_source_nightclub"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: datetime | None = Field(default=None)
    order: "NightclubOrder" = Relationship(
        back_populates="payment", sa_relationship_kwargs={"uselist": False}
    )
    user: Optional["UserPublic"] = Relationship(back_populates="nightclub_payments")


class PaymentOrderQSR(PaymentBase, table=True):
    __tablename__ = "payment_source_qsr"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: datetime | None = Field(default=None)
    order: "QSROrder" = Relationship(
        back_populates="payment", sa_relationship_kwargs={"uselist": False}
    )
    user: Optional["UserPublic"] = Relationship(back_populates="qsr_payments")


class PaymentOrderRestaurant(PaymentBase, table=True):
    __tablename__ = "payment_source_restaurant"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: datetime | None = Field(default=None)
    order: "RestaurantOrder" = Relationship(
        back_populates="payment", sa_relationship_kwargs={"uselist": False}
    )
    user: Optional["UserPublic"] = Relationship(back_populates="restaurant_payments")


class PaymentEvent(PaymentBase, table=True):
    __tablename__ = "payment_event"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    event_booking_id: uuid.UUID | None = Field(
        default=None, foreign_key="event_booking.id"
    )
    event_booking: Optional["EventBooking"] = Relationship(
        back_populates="payment", sa_relationship_kwargs={"uselist": False}
    )
    user: Optional["UserPublic"] = Relationship(back_populates="event_payments")
