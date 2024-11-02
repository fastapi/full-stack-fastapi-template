from sqlmodel import SQLModel

# Import all your models here
from .carousel_poster import CarouselPoster
from .club_visit import ClubVisit
from .event import Event
from .event_booking import EventBooking
from .event_offering import EventOffering
from .group import Group
from .group_wallet import GroupWallet
from .group_wallet_topup import GroupWalletTopup
from .menu import Menu
from .order import NightclubOrder, QSROrder, RestaurantOrder
from .order_item import OrderItem
from .payment import (
    PaymentEvent,
    PaymentOrderNightclub,
    PaymentOrderQSR,
    PaymentOrderRestaurant,
)
from .pickup_location import PickupLocation
from .qrcode import QRCode
from .user import UserBusiness, UserPublic
from .venue import QSR, Foodcourt, Nightclub, Restaurant

# Make all models accessible when importing app.models
__all__ = [
    "SQLModel",
    "ClubVisit",
    "Event",
    "EventBooking",
    "EventOffering",
    "Group",
    "GroupWallet",
    "GroupWalletTopup",
    "Menu",
    "NightclubOrder",
    "RestaurantOrder",
    "QSROrder",
    "OrderItem",
    "PickupLocation",
    "UserBusiness",
    "UserPublic",
    "Nightclub",
    "QSR",
    "Restaurant",
    "Foodcourt",
    "PaymentOrderNightclub",
    "PaymentOrderRestaurant",
    "PaymentOrderQSR",
    "PaymentEvent",
    "QRCode",
    "CarouselPoster",
]


print("target_metadata in init:", SQLModel.metadata.tables)
