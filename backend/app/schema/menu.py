from typing import List, Optional
import uuid
from pydantic import BaseModel, Field

class MenuItemCreate(BaseModel):
    subcategory_id: uuid.UUID
    name: str 
    price: float 
    description: Optional[str] = None
    image_url: Optional[str] = None    
    is_veg: Optional[bool] = None 
    ingredients: Optional[str] = None 
    abv: Optional[float] = None 
    ibu: Optional[int] = None 
    class Config:
        from_attributes = True
# Response schema for a menu item
class MenuItemRead(BaseModel):
    item_id: uuid.UUID
    subcategory_id: uuid.UUID
    name: str 
    price: float 
    description: Optional[str] = None
    image_url: Optional[str] = None    
    is_veg: Optional[bool] = None 
    ingredients: Optional[str] = None 
    abv: Optional[float] = None 
    ibu: Optional[int] = None 
    class Config:
        from_attributes = True
        
class MenuItemUpdate(BaseModel):
    name: Optional[str] = None  # Name can be updated
    price: Optional[float] = None  # Price can be updated
    description: Optional[str] = None  # Description is optional and updatable
    image_url: Optional[str] = None  # Image URL is optional and updatable
    is_veg: Optional[bool] = None  # Optionally update veg/non-veg status
    ingredients: Optional[str] = None  # Ingredients list is optional and updatable
    abv: Optional[float] = None  # Alcohol by volume can be updated
    ibu: Optional[int] = None  # International Bitterness Units can be updated

    class Config:
        from_attributes = True


#########################################################################################################

class MenuSubCategoryCreate(BaseModel):
    name: str  # Name of the subcategory
    is_alcoholic: bool = Field(default=False)
    category_id: uuid.UUID  # Foreign key to the parent category
    class Config:
        from_attributes = True

class MenuSubCategoryRead(BaseModel):
    subcategory_id: uuid.UUID  # Unique identifier for the subcategory
    category_id: uuid.UUID
    is_alcoholic: bool 
    name: str  # Name of the subcategory
    menu_items: Optional[List[MenuItemRead]] = []  # List of items under this subcategory
        
class MenuSubCategoryUpdate(BaseModel):
    name: Optional[str] = None  # Optional name for update
    is_alcoholic: Optional[bool] = None  # Optional field for update
    category_id: Optional[uuid.UUID] = None  # Optional foreign key to update category
    menu_items: Optional[List["MenuItemUpdate"]] = []  # Optional list for updating menu items

    class Config:
        from_attributes = True

#########################################################################################################
class MenuCategoryRead(BaseModel):
    category_id: uuid.UUID  # Unique identifier for the category
    name: str  # Name of the category
    menu_id : uuid.UUID
    sub_categories: List[MenuSubCategoryRead] = []  # List of subcategories

class MenuCategoryCreate(BaseModel):
    name: str  # Name of the category
    menu_id: uuid.UUID
    class Config:
        from_attributes = True

class MenuCategoryUpdate(BaseModel):
    name: Optional[str] = None  # Category name can be updated
    menu_id: Optional[uuid.UUID] = None  # Menu ID can be updated

    class Config:
        from_attributes = True
    
#########################################################################################################
class MenuRead(BaseModel):
    menu_id: uuid.UUID  # Unique identifier for the menu
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: Optional[str] = None  # Description of the menu
    categories: List[MenuCategoryRead] = []  # Nested list of categories
    venue_id: uuid.UUID  # Foreign key to the venue
    menu_type: Optional[str] = None 
    class Config:
       from_attributes = True 

class MenuCreate(BaseModel):
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: Optional[str] = None  # Description of the menu
    venue_id: uuid.UUID  # Foreign key to the venue
    menu_type: Optional[str] = None   # Type of menu (e.g., "Food", "Drink")
    class Config:
        from_attributes = True 
        
class MenuUpdate(BaseModel):
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: Optional[str] = None  # Description of the menu
    menu_type: Optional[str] = None   # Type of menu (e.g., "Food", "Drink")
    class Config:
       from_attributes = True
        