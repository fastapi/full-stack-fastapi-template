import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import model_validator

class MenuCategoryBase(SQLModel):
    qsr_menu_id: Optional[uuid.UUID] = Field(default=None, foreign_key="qsr_menu.id")
    restaurant_menu_id: Optional[uuid.UUID] = Field(default=None, foreign_key="restaurant_menu.id")
    nightclub_menu_id: Optional[uuid.UUID] = Field(default=None, foreign_key="nightclub_menu.id")
    name: str = Field(nullable=False)

    @model_validator(mode="before")
    def check_only_one_menu_id(cls, values):
        # Convert to a regular dictionary
        values_dict = dict(values)
        print("values ", values_dict)

        # Use .get() to safely access values
        qsr_menu_id = values_dict.get('qsr_menu_id')
        restaurant_menu_id = values_dict.get('restaurant_menu_id')
        nightclub_menu_id = values_dict.get('nightclub_menu_id')

        # Count how many of these fields are set (not None)
        menu_ids = [qsr_menu_id, restaurant_menu_id, nightclub_menu_id]
        if sum(id is not None for id in menu_ids) != 1:
            raise ValueError("You must set exactly one of qsr_menu_id, restaurant_menu_id, or nightclub_menu_id.")
        
        return values
    
class MenuCategory(MenuCategoryBase, table=True):
    __tablename__ = "menu_category"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    # Relationships
    menu_items: List["MenuItem"] = Relationship(back_populates="category")

    # Relationships with specific menu types
    qsr_menu: Optional["QSRMenu"] = Relationship(back_populates="categories")
    restaurant_menu: Optional["RestaurantMenu"] = Relationship(back_populates="categories")
    nightclub_menu: Optional["NightclubMenu"] = Relationship(back_populates="categories")