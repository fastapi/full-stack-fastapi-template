from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# Request schema for creating a menu item
class MenuItemCreate(BaseModel):
    category_id: uuid.UUID 
    subcategory_id: Optional[uuid.UUID] = None 
    name: str 
    price: float 
    description: Optional[str] = None
    image_url: Optional[str] = None    
    is_veg: Optional[bool] = None 
    ingredients: Optional[str] = None 
    abv: Optional[float] = None 
    ibu: Optional[int] = None 

# Response schema for a menu item
class MenuItemRead(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID 
    subcategory_id: Optional[uuid.UUID] = None 
    name: str 
    price: float 
    description: Optional[str] = None
    image_url: Optional[str] = None    
    is_veg: Optional[bool] = None 
    ingredients: Optional[str] = None 
    abv: Optional[float] = None 
    ibu: Optional[int] = None 
