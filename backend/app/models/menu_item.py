from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class MenuItemBase(SQLModel):
    category_id: int = Field(foreign_key="menu_category.id", nullable=False)
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    is_veg: Optional[bool] = Field(default=None)
    ingredients: Optional[str] = Field(default=None)
    abv: Optional[float] = Field(default=None)
    ibu: Optional[int] = Field(default=None)

class MenuItem(MenuItemBase, table=True):
    __tablename__="menu_item"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Relationships
    category: Optional["MenuCategory"] = Relationship(back_populates="menu_items")