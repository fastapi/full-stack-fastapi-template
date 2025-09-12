"""Data models for the application."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    STRING_MAX_LENGTH,
)

# Token type constant to avoid hardcoded string
TOKEN_TYPE_BEARER = "bearer"  # noqa: S105


# Shared properties
class UserBase(SQLModel):
    """Base user model with shared fields."""

    email: EmailStr = Field(unique=True, index=True, max_length=EMAIL_MAX_LENGTH)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=STRING_MAX_LENGTH)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


class UserRegister(SQLModel):
    """User registration model."""

    email: EmailStr = Field(max_length=EMAIL_MAX_LENGTH)
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    full_name: str | None = Field(default=None, max_length=STRING_MAX_LENGTH)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """User update model."""

    email: EmailStr | None = Field(default=None, max_length=STRING_MAX_LENGTH)  # type: ignore[assignment]
    password: str | None = Field(
        default=None,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


class UserUpdateMe(SQLModel):
    """User self-update model."""

    full_name: str | None = Field(default=None, max_length=STRING_MAX_LENGTH)
    email: EmailStr | None = Field(default=None, max_length=STRING_MAX_LENGTH)


class UpdatePassword(SQLModel):
    """Password update model."""

    current_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """Database user model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    item_list: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    wallets: list["Wallet"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """Public user model for API responses."""

    id: uuid.UUID


class UsersPublic(SQLModel):
    """Collection of public users."""

    user_data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    """Base item model with shared fields."""

    title: str = Field(min_length=1, max_length=STRING_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=STRING_MAX_LENGTH)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Item creation model."""


# Properties to receive on item update
class ItemUpdate(ItemBase):
    """Item update model."""

    title: str | None = Field(default=None, min_length=1, max_length=STRING_MAX_LENGTH)  # type: ignore[assignment]


# Database model, database table inferred from class name
class Item(ItemBase, table=True):  # noqa: WPS110
    """Database item model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: User | None = Relationship(back_populates="item_list")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """Public item model for API responses."""

    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """Collection of public items."""

    item_data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    """Generic message model."""

    message: str


# JSON payload containing access token
class Token(SQLModel):
    """JWT token model."""

    access_token: str
    token_type: str = TOKEN_TYPE_BEARER


# Contents of JWT token
class TokenPayload(SQLModel):
    """JWT token payload model."""

    sub: str | None = None


class NewPassword(SQLModel):
    """New password model."""

    token: str
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )


# Wallet and Transaction models


class CurrencyEnum(str, Enum):
    """Available currency types."""

    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class TransactionTypeEnum(str, Enum):
    """Transaction type enum."""

    CREDIT = "credit"
    DEBIT = "debit"


# Shared properties for Wallet
class WalletBase(SQLModel):
    """Base wallet model with shared fields."""

    currency: CurrencyEnum = Field(description="Wallet currency")
    balance: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        description="Wallet balance",
    )


# Properties to receive via API on wallet creation
class WalletCreate(SQLModel):
    """Wallet creation model."""

    currency: CurrencyEnum


# Properties to receive via API on wallet update
class WalletUpdate(SQLModel):
    """Wallet update model."""

    balance: Decimal | None = Field(default=None, decimal_places=2)


# Database model for Wallet
class Wallet(WalletBase, table=True):
    """Database wallet model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: User | None = Relationship(back_populates="wallets")
    transactions: list["Transaction"] = Relationship(
        back_populates="wallet",
        cascade_delete=True,
    )


# Properties to return via API
class WalletPublic(WalletBase):
    """Public wallet model for API responses."""

    id: uuid.UUID
    user_id: uuid.UUID


class WalletsPublic(SQLModel):
    """Collection of public wallets."""

    wallet_data: list[WalletPublic]
    count: int


# Shared properties for Transaction
class TransactionBase(SQLModel):
    """Base transaction model with shared fields."""

    amount: Decimal = Field(decimal_places=2, description="Transaction amount")
    type: TransactionTypeEnum = Field(description="Transaction type")
    currency: CurrencyEnum = Field(description="Transaction currency")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Transaction timestamp",
    )


# Properties to receive via API on transaction creation
class TransactionCreate(SQLModel):
    """Transaction creation model."""

    wallet_id: uuid.UUID
    amount: Decimal = Field(
        decimal_places=2,
        gt=0,
        description="Transaction amount must be positive",
    )
    type: TransactionTypeEnum
    currency: CurrencyEnum


# Database model for Transaction
class Transaction(TransactionBase, table=True):
    """Database transaction model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    wallet_id: uuid.UUID = Field(
        foreign_key="wallet.id",
        nullable=False,
        ondelete="CASCADE",
    )
    wallet: Wallet | None = Relationship(back_populates="transactions")


# Properties to return via API
class TransactionPublic(TransactionBase):
    """Public transaction model for API responses."""

    id: uuid.UUID
    wallet_id: uuid.UUID


class TransactionsPublic(SQLModel):
    """Collection of public transactions."""

    transaction_data: list[TransactionPublic]
    count: int
