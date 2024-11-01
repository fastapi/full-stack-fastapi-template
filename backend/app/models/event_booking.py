import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.event_offering import EventOffering
    from app.models.payment import PaymentEvent
    from app.models.user import UserPublic


class EventBooking(SQLModel, table=True):
    __tablename__ = "event_booking"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(foreign_key="user_public.id", nullable=False)
    event_id: uuid.UUID | None = Field(foreign_key="event.id", nullable=False)
    booking_time: datetime = Field(nullable=False)
    total_amount: float = Field(nullable=False)
    status: str = Field(nullable=False)

    # Relationships
    user: Optional["UserPublic"] = Relationship(back_populates="event_bookings")
    event: Optional["Event"] = Relationship(back_populates="event_bookings")
    payment: Optional["PaymentEvent"] = Relationship(
        back_populates="event_booking", sa_relationship_kwargs={"uselist": False}
    )
    event_offerings: list["EventOffering"] = Relationship(
        back_populates="event_booking"
    )
