from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class MenuBase(SQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    menu_type: Optional[str] = Field(default=None)  # Type of menu (e.g., "Food", "Drink")

class QSRMenuBase(MenuBase):
    qsr_id: int = Field(foreign_key="qsr.id", nullable=False)

class QSRMenu(QSRMenuBase, table=True):
    __tablename__= "qsr_menu"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    qsr: "QSR" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="qsr_menu")

class RestaurantMenuBase(MenuBase):
    restaurant_id: int = Field(foreign_key="restaurant.id", nullable=False)

class RestaurantMenu(RestaurantMenuBase, table=True):
    __tablename__= "restaurant_menu"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="restaurant_menu")

class NightclubMenuBase(MenuBase):
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)

class NightclubMenu(NightclubMenuBase, table=True):
    __tablename__= "nightclub_menu"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    nightclub: "Nightclub" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="nightclub_menu")
