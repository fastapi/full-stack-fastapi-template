from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class PaymentBase(SQLModel):
    user_id: int = Field(foreign_key="user_public.id", nullable=False)
    source_type: str = Field(nullable=False)  # Changed to str
    gateway_transaction_id: Optional[int] = Field(default=None)
    payment_time: datetime = Field(nullable=False)
    amount: float = Field(nullable=False)
    status: str = Field(nullable=False)  # e.g., Paid, Pending, Failed
    source_type: str = Field(nullable=False)

class PaymentOrderNightclub(PaymentBase, table=True):
    __tablename__ = "payment_source_nightclub"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: Optional[datetime] = Field(default=None)
    order: "NightclubOrder" = Relationship(back_populates="payment", sa_relationship_kwargs={"uselist": False})
    user: Optional["UserPublic"] = Relationship(back_populates="nightclub_payments")

class PaymentOrderQSR(PaymentBase, table=True):
    __tablename__ = "payment_source_qsr"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: Optional[datetime] = Field(default=None)
    order: "QSROrder" = Relationship(back_populates="payment", sa_relationship_kwargs={"uselist": False})
    user: Optional["UserPublic"] = Relationship(back_populates="qsr_payments")

class PaymentOrderRestaurant(PaymentBase, table=True):
    __tablename__ = "payment_source_restaurant"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    retry_count: int = Field(default=0)
    last_attempt_time: Optional[datetime] = Field(default=None)
    order: "RestaurantOrder" = Relationship(back_populates="payment", sa_relationship_kwargs={"uselist": False})
    user: Optional["UserPublic"] = Relationship(back_populates="restaurant_payments")

class PaymentEvent(PaymentBase, table=True):
    __tablename__ = "payment_event"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    event_booking_id: Optional[int] = Field(default=None, foreign_key="event_booking.id")
    event_booking: Optional["EventBooking"] = Relationship(back_populates="payment", sa_relationship_kwargs={"uselist": False})
    user: Optional["UserPublic"] = Relationship(back_populates="event_payments")
