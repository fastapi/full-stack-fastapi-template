import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base_model import BaseTimeModel

if TYPE_CHECKING:
    from app.models.venue import Venue

from app.schema.menu import (
    MenuCategoryCreate,
    MenuCategoryRead,
    MenuCreate,
    MenuItemCreate,
    MenuItemRead,
    MenuRead,
    MenuSubCategoryCreate,
    MenuSubCategoryRead,
)


class MenuItem(BaseTimeModel, table=True):
    __tablename__ = "menu_item"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    subcategory_id: uuid.UUID = Field(foreign_key="menu_subcategory.id", nullable=False)
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)
    description: str | None = Field(default=None)
    image_url: str | None = Field(default=None)
    is_veg: bool | None = Field(default=None)
    ingredients: str | None = Field(default=None)
    abv: float | None = Field(default=None)
    ibu: int | None = Field(default=None)

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
            ibu=schema.ibu,
        )

    @classmethod
    def to_read_schema(self) -> MenuItemRead:
        return MenuItemRead(
            item_id=self.id,
            subcategory_id=self.subcategory_id,
            name=self.name,
            price=self.price,
            description=self.description,
            image_url=self.image_url,
            is_veg=self.is_veg,
            ingredients=self.ingredients,
            abv=self.abv,
            ibu=self.ibu,
        )


#########################################################################################################


class MenuSubCategory(BaseTimeModel, table=True):
    __tablename__ = "menu_subcategory"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    category_id: uuid.UUID = Field(foreign_key="menu_category.id", nullable=False)
    name: str = Field(nullable=False)
    is_alcoholic: bool = Field(default=False)

    # Relationships
    category: "MenuCategory" = Relationship(back_populates="sub_categories")
    menu_items: list["MenuItem"] = Relationship(back_populates="subcategory")

    @classmethod
    def from_create_schema(cls, schema: "MenuSubCategoryCreate") -> "MenuSubCategory":
        return cls(
            name=schema.name,
            category_id=schema.category_id,
            is_alcoholic=schema.is_alcoholic,  # Include is_alcoholic in the model
        )

    @classmethod
    def to_read_schema(self) -> MenuSubCategoryRead:
        return MenuSubCategoryRead(
            subcategory_id=self.id,
            category_id=self.category_id,
            name=self.name,
            is_alcoholic=self.is_alcoholic,
            menu_items=[item.to_read_schema() for item in self.menu_items],
        )


#########################################################################################################


class MenuCategory(BaseTimeModel, table=True):
    __tablename__ = "menu_category"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    menu_id: uuid.UUID = Field(foreign_key="menu.id", nullable=False)
    name: str = Field(nullable=False)

    # Relationships
    menu: "Menu" = Relationship(back_populates="categories")
    sub_categories: list["MenuSubCategory"] = Relationship(back_populates="category")

    @classmethod
    def from_create_schema(cls, schema: MenuCategoryCreate) -> "MenuCategory":
        return cls(name=schema.name, menu_id=schema.menu_id)

    @classmethod
    def to_read_schema(cls, self) -> MenuCategoryRead:
        return MenuCategoryRead(
            category_id=self.id,
            menu_id=self.menu_id,
            name=self.name,
            sub_categories=[
                subcategory.to_read_schema() for subcategory in self.sub_categories
            ],
        )


#########################################################################################################


class Menu(BaseTimeModel, table=True):
    __tablename__ = "menu"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    menu_type: str | None = Field(default=None)  # Type of menu (e.g., "Food", "Drink")
    venue_id: uuid.UUID = Field(foreign_key="venue.id", nullable=False)

    # Relationships
    categories: list["MenuCategory"] = Relationship(back_populates="menu")
    venue: "Venue" = Relationship(back_populates="menu")

    @classmethod
    def from_create_schema(cls, schema: MenuCreate) -> "Menu":
        return cls(
            name=schema.name,
            description=schema.description,
            menu_type=schema.menu_type,
            venue_id=schema.venue_id,
        )

    def to_read_schema(self) -> MenuRead:
        return MenuRead(
            menu_id=self.id,
            name=self.name,
            description=self.description,
            menu_type=self.menu_type,
            venue_id=self.venue_id,
            categories=[
                MenuCategory.to_read_schema(category) for category in self.categories
            ],
        )


#########################################################################################################
