from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class MenuCategory(SQLModel, table=True):
    __tablename__ = "menu_category"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # Foreign keys for different menus
    qsr_menu_id: Optional[int] = Field(default=None, foreign_key="qsrmenu.id")
    restaurant_menu_id: Optional[int] = Field(default=None, foreign_key="restaurantmenu.id")
    nightclub_menu_id: Optional[int] = Field(default=None, foreign_key="nightclubmenu.id")

    name: str = Field(nullable=False)

    # Relationships
    menu_items: List["MenuItem"] = Relationship(back_populates="category")

    # Relationships with specific menu types
    qsr_menu: Optional["QSRMenu"] = Relationship(back_populates="categories")
    restaurant_menu: Optional["RestaurantMenu"] = Relationship(back_populates="categories")
    nightclub_menu: Optional["NightclubMenu"] = Relationship(back_populates="categories")