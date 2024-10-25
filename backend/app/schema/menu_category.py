from typing import List, Optional
import uuid
from app.schema.menu_item import MenuItemCreate, MenuItemRead
from pydantic import BaseModel


class MenuCategoryRead(BaseModel):
    name: str  # Name of the category
    menu_items: Optional[List[MenuItemRead]] = []  # List of items under this category
    sub_categories: Optional[List["MenuSubCategoryRead"]] = []  # List of subcategories

# Forward declaration for subcategory read schema to avoid circular imports
class MenuSubCategoryRead(BaseModel):
    id: uuid.UUID  # Unique identifier for the subcategory
    name: str  # Name of the subcategory
    menu_items: Optional[List[MenuItemRead]] = []  # List of items under this subcategory

class MenuCategoryCreate(BaseModel):
    name: str  # Name of the category
    menu_items: Optional[List[MenuItemCreate]] = []  # List of items under this category
    sub_categories: Optional[List["MenuSubCategoryCreate"]] = []  # List of subcategories

# Forward declaration for subcategory to avoid circular imports
class MenuSubCategoryCreate(BaseModel):
    name: str  # Name of the subcategory
    category_id: uuid.UUID  # Foreign key to the parent category
    menu_items: Optional[List[MenuItemCreate]] = []  # List of items under this subcategory