from typing import List, Optional
import uuid
from app.models.menu import NightclubMenuBase, QSRMenuBase, RestaurantMenuBase
from app.models.menu_item import MenuItemBase
from app.models.menu_category import MenuCategoryBase

class QSRMenuRead(QSRMenuBase):
    id: Optional[uuid.UUID]
    class Config:
        from_attributes = True

class QSRMenuCreate(QSRMenuBase):
    class Config:
        from_attributes = True

class RestaurantMenuRead(RestaurantMenuBase):
    id: Optional[uuid.UUID]
    class Config:
        from_attributes = True

class RestaurantMenuCreate(RestaurantMenuBase):
    class Config:
        from_attributes = True

class MenuItemRead(MenuItemBase):
    id: Optional[uuid.UUID]
    class Config:
        from_attributes = True

class MenuCategoryRead(MenuCategoryBase):
    id: Optional[uuid.UUID]
    menu_items: List[MenuItemRead] = []
    class Config:
        from_attributes = True

class NightclubMenuRead(NightclubMenuBase):
    id: Optional[uuid.UUID]
    categories: List[MenuCategoryRead] = []
    class Config:
        from_attributes = True

class MenuItemCreate(MenuItemBase):
    class Config:
        from_attributes = True

class MenuCategoryCreate(MenuCategoryBase):
    class Config:
        from_attributes = True

class NightclubMenuCreate(NightclubMenuBase):
    class Config:
        from_attributes = True
