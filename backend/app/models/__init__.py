from sqlmodel import SQLModel

# Import all your models here
from .club_visit import ClubVisit
from .event import Event
from .event_booking import EventBooking
from .event_offering import EventOffering
from .group import Group
from .group_wallet import GroupWallet
from .group_wallet_topup import GroupWalletTopup
from .menu import RestaurantMenu, NightclubMenu, QSRMenu
from .menu_category import MenuCategory
from .menu_item import MenuItem
from .order import NightclubOrder, RestaurantOrder, QSROrder
from .order_item import OrderItem
from .pickup_location import PickupLocation
from .user import UserBusiness, UserPublic
from .venue import Nightclub, QSR, Restaurant, Foodcourt
from .payment import  PaymentOrderNightclub, PaymentOrderRestaurant, PaymentOrderQSR, PaymentEvent

# Make all models accessible when importing app.models
__all__ = [
    "SQLModel", "ClubVisit", "Event", "EventBooking", "EventOffering", "Group", "GroupWallet", 
    "GroupWalletTopup", "RestaurantMenu", "NightclubMenu", "QSRMenu", "MenuCategory", 
    "MenuItem", "NightclubOrder", "RestaurantOrder", "QSROrder", "OrderItem", 
    "PickupLocation", "UserBusiness", "UserPublic", "Nightclub", "QSR", "Restaurant", 
    "Foodcourt", "PaymentOrderNightclub", "PaymentOrderRestaurant", "PaymentOrderQSR", 
    "PaymentEvent"
]


print("target_metadata in init:", SQLModel.metadata.tables)