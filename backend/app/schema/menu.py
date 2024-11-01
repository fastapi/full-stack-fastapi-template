import uuid

from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    subcategory_id: uuid.UUID
    name: str
    price: float
    description: str | None = None
    image_url: str | None = None
    is_veg: bool | None = None
    ingredients: str | None = None
    abv: float | None = None
    ibu: int | None = None

    class Config:
        from_attributes = True


# Response schema for a menu item
class MenuItemRead(BaseModel):
    item_id: uuid.UUID
    subcategory_id: uuid.UUID
    name: str
    price: float
    description: str | None = None
    image_url: str | None = None
    is_veg: bool | None = None
    ingredients: str | None = None
    abv: float | None = None
    ibu: int | None = None

    class Config:
        from_attributes = True


class MenuItemUpdate(BaseModel):
    name: str | None = None  # Name can be updated
    price: float | None = None  # Price can be updated
    description: str | None = None  # Description is optional and updatable
    image_url: str | None = None  # Image URL is optional and updatable
    is_veg: bool | None = None  # Optionally update veg/non-veg status
    ingredients: str | None = None  # Ingredients list is optional and updatable
    abv: float | None = None  # Alcohol by volume can be updated
    ibu: int | None = None  # International Bitterness Units can be updated

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
    menu_items: list[MenuItemRead] | None = []  # list of items under this subcategory


class MenuSubCategoryUpdate(BaseModel):
    name: str | None = None  # Optional name for update
    is_alcoholic: bool | None = None  # Optional field for update
    category_id: uuid.UUID | None = None  # Optional foreign key to update category
    menu_items: list["MenuItemUpdate"] | None = (
        []
    )  # Optional list for updating menu items

    class Config:
        from_attributes = True


#########################################################################################################
class MenuCategoryRead(BaseModel):
    category_id: uuid.UUID  # Unique identifier for the category
    name: str  # Name of the category
    menu_id: uuid.UUID
    sub_categories: list[MenuSubCategoryRead] = []  # list of subcategories


class MenuCategoryCreate(BaseModel):
    name: str  # Name of the category
    menu_id: uuid.UUID

    class Config:
        from_attributes = True


class MenuCategoryUpdate(BaseModel):
    name: str | None = None  # Category name can be updated
    menu_id: uuid.UUID | None = None  # Menu ID can be updated

    class Config:
        from_attributes = True


#########################################################################################################
class MenuRead(BaseModel):
    menu_id: uuid.UUID  # Unique identifier for the menu
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: str | None = None  # Description of the menu
    categories: list[MenuCategoryRead] = []  # Nested list of categories
    venue_id: uuid.UUID  # Foreign key to the venue
    menu_type: str | None = None

    class Config:
        from_attributes = True


class MenuCreate(BaseModel):
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: str | None = None  # Description of the menu
    venue_id: uuid.UUID  # Foreign key to the venue
    menu_type: str | None = None  # Type of menu (e.g., "Food", "Drink")

    class Config:
        from_attributes = True


class MenuUpdate(BaseModel):
    name: str  # Name of the menu (could be a restaurant menu or type of menu)
    description: str | None = None  # Description of the menu
    menu_type: str | None = None  # Type of menu (e.g., "Food", "Drink")

    class Config:
        from_attributes = True
