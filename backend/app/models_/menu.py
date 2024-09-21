from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

from app.models.menu_item import MenuItem
from app.models.venue import QSR, Nightclub, Restaurant


# Base class for Menu
class MenuBase(SQLModel):
    name: str = Field(nullable=True)
    description: Optional[str] = Field(default=None)

# Schema for reading a Menu
class MenuRead(SQLModel):
    id: int
    name: str
    description: Optional[str]

# Schema for creating a Menu (excluding the ID which is auto-generated)
class MenuCreate(SQLModel):
    name: str
    description: Optional[str]
    menu_type: Optional[str]


# QSR Menu model
class QSRMenu(MenuBase, table=True):
    __tablename__ = "qsr_menu"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    qsr_id: int = Field(foreign_key="qsr.id", nullable=False)

    # Relationships
    qsr: "QSR" = Relationship(back_populates="menu")
    categories:  List["menu_category"] = Relationship(back_populates="qsr_menu")


# Schema for reading a QSR Menu
class QSRMenuRead(MenuRead):
    qsr_id: int


# Schema for creating a QSR Menu
class QSRMenuCreate(MenuCreate):
    qsr_id: int


# Restaurant Menu model
class RestaurantMenu(MenuBase, table=True):
    __tablename__ = "restaurant_menu"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    restaurant_id: int = Field(foreign_key="restaurant.id", nullable=False)

    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="menu")
    categories:  List["menu_category"] = Relationship(back_populates="restaurant_menu")


# Schema for reading a Restaurant Menu
class RestaurantMenuRead(MenuRead):
    restaurant_id: int


# Schema for creating a Restaurant Menu
class RestaurantMenuCreate(MenuCreate):
    restaurant_id: int


# Nightclub Menu model
class NightclubMenu(MenuBase, table=True):
    __tablename__ = "nightclub_menu"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)

    # Relationships
    nightclub: "Nightclub" = Relationship(back_populates="menu")
    categories:  List["menu_category"] = Relationship(back_populates="nightclub_menu")


# Schema for reading a Nightclub Menu
class NightclubMenuRead(MenuRead):
    nightclub_id: int


# Schema for creating a Nightclub Menu
class NightclubMenuCreate(MenuCreate):
    nightclub_id: int