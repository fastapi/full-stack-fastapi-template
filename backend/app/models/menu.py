import uuid
from app.schema.menu import MenuCategoryCreate, MenuCategoryRead, MenuCreate, MenuItemCreate, MenuItemRead, MenuRead, MenuSubCategoryCreate, MenuSubCategoryRead
from pydantic import ValidationError
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_item"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    subcategory_id: uuid.UUID = Field(foreign_key="menu_subcategory.id",nullable=False)
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    is_veg: Optional[bool] = Field(default=None)
    ingredients: Optional[str] = Field(default=None)
    abv: Optional[float] = Field(default=None)
    ibu: Optional[int] = Field(default=None)

    # Relationships
    subcategory: Optional["MenuSubCategory"] = Relationship(back_populates="menu_items")

    @classmethod
    def from_create_schema(cls, schema: MenuItemCreate) -> "MenuItem":
        return cls(
            subcategory_id=schema.subcategory_id,
            name=schema.name,
            price=schema.price,
            description=schema.description,
            image_url=schema.image_url,
            is_veg=schema.is_veg,
            ingredients=schema.ingredients,
            abv=schema.abv,
            ibu=schema.ibu
        )

    @classmethod
    def to_read_schema(cls, item: "MenuItem") -> MenuItemRead:
        return MenuItemRead(
            item_id=item.id,
            subcategory_id=item.subcategory_id,
            name=item.name,
            price=item.price,
            description=item.description,
            image_url=item.image_url,
            is_veg=item.is_veg,
            ingredients=item.ingredients,
            abv=item.abv,
            ibu=item.ibu
        )

#########################################################################################################

class MenuSubCategory(SQLModel, table=True):
    __tablename__ = "menu_subcategory"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    category_id: uuid.UUID = Field(foreign_key="menu_category.id", nullable=False)
    name: str = Field(nullable=False)
    is_alcoholic: bool = Field(default=False)

    # Relationships
    category: "MenuCategory" = Relationship(back_populates="sub_categories")
    menu_items: List["MenuItem"] = Relationship(back_populates="subcategory")

    @classmethod
    def from_create_schema(cls, schema: "MenuSubCategoryCreate") -> "MenuSubCategory":
        return cls(
            name=schema.name,
            category_id=schema.category_id,
            is_alcoholic=schema.is_alcoholic  # Include is_alcoholic in the model
        )

    @classmethod
    def to_read_schema(cls, subcategory: "MenuSubCategory") -> MenuSubCategoryRead:
        return MenuSubCategoryRead(
            subcategory_id=subcategory.id,
            category_id=subcategory.category_id,
            name=subcategory.name,
            is_alcoholic=subcategory.is_alcoholic,
            menu_items=[MenuItem.to_read_schema(item) for item in subcategory.menu_items]
        )

#########################################################################################################

class MenuCategory(SQLModel, table=True):
    __tablename__ = "menu_category"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    menu_id: uuid.UUID = Field(foreign_key="menu.id", nullable=False)
    name: str = Field(nullable=False)

    # Relationships
    menu: "Menu" = Relationship(back_populates="categories")
    sub_categories: List["MenuSubCategory"] = Relationship(back_populates="category")

    @classmethod
    def from_create_schema(cls, schema: MenuCategoryCreate) -> "MenuCategory":
        return cls(
            name=schema.name,
            menu_id=schema.menu_id
        )

    @classmethod
    def to_read_schema(cls, category: "MenuCategory") -> MenuCategoryRead:
        return MenuCategoryRead(
            category_id=category.id,
            menu_id=category.menu_id,
            name=category.name,
            sub_categories=[MenuSubCategory.to_read_schema(subcategory) for subcategory in category.sub_categories]
        )

#########################################################################################################

class Menu(SQLModel, table=True):
    __tablename__ = "menu"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    menu_type: Optional[str] = Field(default=None)  # Type of menu (e.g., "Food", "Drink")
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False)

    # Relationships
    categories: List["MenuCategory"] = Relationship(back_populates="menu")
    venue: "Venue" = Relationship(back_populates="menu")
    
    @classmethod
    def from_create_schema(cls, schema: MenuCreate) -> "Menu":
        return cls(
            name=schema.name,
            description=schema.description,
            menu_type=schema.menu_type,
            venue_id=schema.venue_id
        )

    @classmethod
    def to_read_schema(cls, menu: "Menu") -> MenuRead:
        return MenuRead(
            menu_id=menu.id,
            name=menu.name,
            description=menu.description,
            menu_type=menu.menu_type,
            venue_id=menu.venue_id,
            categories=[MenuCategory.to_read_schema(category) for category in menu.categories]
        )

#########################################################################################################