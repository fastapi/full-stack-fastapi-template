import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import EmailStr
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel
from sqlalchemy import JSON, Numeric


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    orders: list["Order"] = Relationship(back_populates="owner", cascade_delete=True)


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
    new_password: str = Field(min_length=8, max_length=128)


# Payment Models
# Shared properties for Order
class OrderBase(SQLModel):
    amount: Decimal = Field(gt=0, description="Amount in smallest currency unit (paise for INR)")
    currency: str = Field(default="INR", max_length=3)
    receipt: str | None = Field(default=None, max_length=255)
    notes: dict[str, str] | None = None


# Properties to receive via API on order creation
class OrderCreate(OrderBase):
    pass


# Properties to receive via API for order creation request
class OrderCreateRequest(SQLModel):
    amount: int = Field(gt=0, description="Amount in smallest currency unit (paise for INR)")
    currency: str = Field(default="INR", max_length=3)
    receipt: str | None = Field(default=None, max_length=255)
    notes: dict[str, str] | None = None


# Database model for Order
class Order(OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    razorpay_order_id: str = Field(unique=True, index=True, max_length=255)
    status: str = Field(
        default="pending",
        max_length=50,
        description="Order status: pending, created, paid, failed, cancelled",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False)),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False)),
    )
    owner: "User" = Relationship(back_populates="orders")
    payments: list["Payment"] = Relationship(back_populates="order", cascade_delete=True)

    # Override amount to use Numeric type in database
    amount: Decimal = Field(
        sa_column=Column(Numeric(precision=19, scale=2)),
        gt=0,
    )

    # Override notes to use JSON type in database
    notes: dict[str, str] | None = Field(
        default=None,
        sa_column=Column(JSON),
    )


# Properties to return via API
class OrderPublic(OrderBase):
    id: uuid.UUID
    user_id: uuid.UUID
    razorpay_order_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class OrderUpdate(SQLModel):
    status: str | None = Field(default=None, max_length=50)
    notes: dict[str, str] | None = None


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int


# Shared properties for Payment
class PaymentBase(SQLModel):
    razorpay_payment_id: str = Field(max_length=255)
    amount: Decimal = Field(gt=0)
    currency: str = Field(max_length=3)
    method: str | None = Field(default=None, max_length=50)


# Properties to receive via API on payment creation
class PaymentCreate(PaymentBase):
    razorpay_signature: str | None = Field(default=None, max_length=500)
    order_id: uuid.UUID


# Properties to receive via API for payment verification
class PaymentVerifyRequest(SQLModel):
    razorpay_order_id: str = Field(max_length=255)
    razorpay_payment_id: str = Field(max_length=255)
    razorpay_signature: str = Field(max_length=500)


# Database model for Payment
class Payment(PaymentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(
        foreign_key="order.id", nullable=False, ondelete="CASCADE"
    )
    razorpay_signature: str | None = Field(default=None, max_length=500)
    status: str = Field(
        default="pending",
        max_length=50,
        description="Payment status: pending, authorized, captured, failed, refunded",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False)),
    )
    order: "Order" = Relationship(back_populates="payments")

    # Override amount to use Numeric type in database
    amount: Decimal = Field(
        sa_column=Column(Numeric(precision=19, scale=2)),
        gt=0,
    )


# Properties to return via API
class PaymentPublic(PaymentBase):
    id: uuid.UUID
    order_id: uuid.UUID
    razorpay_signature: str | None
    status: str
    created_at: datetime


# Response for order creation
class OrderCreateResponse(SQLModel):
    id: str  # razorpay_order_id
    order_id: str  # razorpay_order_id (for backward compatibility)
    amount: int  # in paise
    currency: str
    key: str  # Razorpay Key ID for frontend


# Response for payment verification
class PaymentVerifyResponse(SQLModel):
    success: bool
    order: OrderPublic
    payment: PaymentPublic
