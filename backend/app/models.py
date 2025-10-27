import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Numeric


# Enums for Inventory Management System
class UserRole(str, Enum):
    """Roles de usuario en el sistema de inventario"""
    ADMINISTRADOR = "administrador"
    VENDEDOR = "vendedor"
    AUXILIAR = "auxiliar"


class MovementType(str, Enum):
    """Tipos de movimientos de inventario"""
    ENTRADA_COMPRA = "entrada_compra"
    SALIDA_VENTA = "salida_venta"
    AJUSTE_CONTEO = "ajuste_conteo"
    AJUSTE_MERMA = "ajuste_merma"
    DEVOLUCION_CLIENTE = "devolucion_cliente"
    DEVOLUCION_PROVEEDOR = "devolucion_proveedor"


class AlertType(str, Enum):
    """Tipos de alertas de inventario"""
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.VENDEDOR)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    # Inventory relationships
    categories: list["Category"] = Relationship(back_populates="created_by_user", cascade_delete=True)
    products: list["Product"] = Relationship(back_populates="created_by_user", cascade_delete=True)
    inventory_movements: list["InventoryMovement"] = Relationship(back_populates="created_by_user")
    resolved_alerts: list["Alert"] = Relationship(
        back_populates="resolved_by_user",
        sa_relationship_kwargs={"foreign_keys": "Alert.resolved_by"}
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# ============================================================================
# INVENTORY MANAGEMENT SYSTEM MODELS
# ============================================================================

# Category Models
# ============================================================================

class CategoryBase(SQLModel):
    """Base model for Category with shared properties"""
    name: str = Field(min_length=1, max_length=100, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(SQLModel):
    """Schema for updating a category - all fields optional"""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class Category(CategoryBase, table=True):
    """Database model for Category"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    # Relationships
    created_by_user: User | None = Relationship(back_populates="categories")
    products: list["Product"] = Relationship(back_populates="category")


class CategoryPublic(CategoryBase):
    """Schema for returning category via API"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID


class CategoriesPublic(SQLModel):
    """Schema for returning list of categories"""
    data: list[CategoryPublic]
    count: int


# Product Models
# ============================================================================

class ProductBase(SQLModel):
    """Base model for Product with shared properties"""
    sku: str = Field(min_length=1, max_length=50, unique=True, index=True)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    unit_price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
        gt=0,
        description="Precio de costo/compra"
    )
    sale_price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
        gt=0,
        description="Precio de venta"
    )
    unit_of_measure: str = Field(max_length=50, description="Ej: unidad, kg, litro")
    min_stock: int = Field(ge=0, default=0, description="Stock mínimo para alertas")
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(SQLModel):
    """Schema for updating a product - all fields optional"""
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_id: uuid.UUID | None = None
    unit_price: Decimal | None = Field(default=None, gt=0)
    sale_price: Decimal | None = Field(default=None, gt=0)
    unit_of_measure: str | None = Field(default=None, max_length=50)
    min_stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class Product(ProductBase, table=True):
    """Database model for Product"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    current_stock: int = Field(ge=0, default=0, description="Stock actual")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    # Relationships
    category: Category | None = Relationship(back_populates="products")
    created_by_user: User | None = Relationship(back_populates="products")
    inventory_movements: list["InventoryMovement"] = Relationship(back_populates="product")
    alerts: list["Alert"] = Relationship(back_populates="product", cascade_delete=True)


class ProductPublic(ProductBase):
    """Schema for returning product via API"""
    id: uuid.UUID
    current_stock: int
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID


class ProductsPublic(SQLModel):
    """Schema for returning list of products"""
    data: list[ProductPublic]
    count: int


# InventoryMovement Models
# ============================================================================

class InventoryMovementBase(SQLModel):
    """Base model for InventoryMovement with shared properties"""
    product_id: uuid.UUID
    movement_type: MovementType
    quantity: int = Field(
        ne=0,
        description="Positivo para entradas, negativo para salidas"
    )
    reference_number: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=500)
    unit_price: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
        gt=0
    )
    movement_date: datetime = Field(default_factory=datetime.utcnow)


class InventoryMovementCreate(InventoryMovementBase):
    """Schema for creating a new inventory movement"""
    pass


class InventoryMovement(InventoryMovementBase, table=True):
    """Database model for InventoryMovement"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    total_amount: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True)
    )
    stock_before: int = Field(ge=0)
    stock_after: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    # Relationships
    product: Product | None = Relationship(back_populates="inventory_movements")
    created_by_user: User | None = Relationship(back_populates="inventory_movements")


class InventoryMovementPublic(InventoryMovementBase):
    """Schema for returning inventory movement via API"""
    id: uuid.UUID
    total_amount: Decimal | None
    stock_before: int
    stock_after: int
    created_at: datetime
    created_by: uuid.UUID


class InventoryMovementsPublic(SQLModel):
    """Schema for returning list of inventory movements"""
    data: list[InventoryMovementPublic]
    count: int


# Alert Models
# ============================================================================

class AlertBase(SQLModel):
    """Base model for Alert with shared properties"""
    product_id: uuid.UUID
    alert_type: AlertType
    current_stock: int = Field(ge=0)
    min_stock: int = Field(ge=0)
    notes: str | None = Field(default=None, max_length=500)


class AlertCreate(AlertBase):
    """Schema for creating a new alert"""
    pass


class AlertUpdate(SQLModel):
    """Schema for updating an alert"""
    is_resolved: bool | None = None
    notes: str | None = Field(default=None, max_length=500)


class Alert(AlertBase, table=True):
    """Database model for Alert"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: Product | None = Relationship(back_populates="alerts")
    resolved_by_user: User | None = Relationship(back_populates="resolved_alerts")


class AlertPublic(AlertBase):
    """Schema for returning alert via API"""
    id: uuid.UUID
    is_resolved: bool
    resolved_at: datetime | None
    resolved_by: uuid.UUID | None
    created_at: datetime


class AlertsPublic(SQLModel):
    """Schema for returning list of alerts"""
    data: list[AlertPublic]
    count: int
