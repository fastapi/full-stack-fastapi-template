from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class MenuBase(SQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    menu_type: Optional[str] = Field(default=None)  # Type of menu (e.g., "Food", "Drink")

class QSRMenu(MenuBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    qsr_id: int = Field(foreign_key="qsr.id", nullable=False)

    # Relationships
    qsr: "QSR" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="qsr_menu")


class RestaurantMenu(MenuBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    restaurant_id: int = Field(foreign_key="restaurant.id", nullable=False)

    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="restaurant_menu")


class NightclubMenu(MenuBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nightclub_id: int = Field(foreign_key="nightclub.id", nullable=False)

    # Relationships
    nightclub: "Nightclub" = Relationship(back_populates="menu")
    categories: List["MenuCategory"] = Relationship(back_populates="nightclub_menu")
