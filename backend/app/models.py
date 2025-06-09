import uuid
from typing import Optional, List
from pydantic import EmailStr, Field
from sqlmodel import Relationship, SQLModel
from datetime import datetime
from enum import Enum


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


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
    phone: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime


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


class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    LAND = "land"
    COMMERCIAL = "commercial"
    OFFICE = "office"


class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"
    PENDING = "pending"


class Property(SQLModel):
    id: str
    title: str
    description: str
    price: float
    property_type: PropertyType
    status: PropertyStatus
    address: str
    city: str
    state: str
    zip_code: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    area: float
    features: List[str]
    images: List[str]
    created_at: datetime
    updated_at: datetime
    owner_id: str


class Transaction(SQLModel):
    id: str
    property_id: str
    buyer_id: str
    seller_id: str
    amount: float
    transaction_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class Credit(SQLModel):
    id: str
    user_id: str
    property_id: str
    amount: float
    interest_rate: float
    term_months: int
    status: str
    created_at: datetime
    updated_at: datetime


class Appraisal(SQLModel):
    id: str
    property_id: str
    appraiser_id: str
    value: float
    report_url: str
    status: str
    created_at: datetime
    updated_at: datetime


class ManagementContract(SQLModel):
    id: str
    property_id: str
    owner_id: str
    manager_id: str
    start_date: datetime
    end_date: datetime
    fee_percentage: float
    status: str
    created_at: datetime
    updated_at: datetime


class AdvisorySession(SQLModel):
    id: str
    client_id: str
    advisor_id: str
    topic: str
    notes: str
    status: str
    created_at: datetime
    updated_at: datetime


# Response models
class PropertyResponse(SQLModel):
    id: str
    title: str
    description: str
    price: float
    property_type: PropertyType
    status: PropertyStatus
    address: str
    city: str
    state: str
    zip_code: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    area: float
    features: List[str]
    images: List[str]
    created_at: datetime
    updated_at: datetime
    owner: User
    transactions: List[Transaction]
    appraisals: List[Appraisal]


class UserResponse(SQLModel):
    id: str
    email: EmailStr
    full_name: str
    phone: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime
    properties: List[Property]
    transactions: List[Transaction]
    credits: List[Credit]


class TransactionResponse(SQLModel):
    id: str
    property_id: str
    buyer_id: str
    seller_id: str
    amount: float
    transaction_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    property: Property
    buyer: User
    seller: User


class CreditResponse(SQLModel):
    id: str
    user_id: str
    property_id: str
    amount: float
    interest_rate: float
    term_months: int
    status: str
    created_at: datetime
    updated_at: datetime
    user: User
    property: Property


class AppraisalResponse(SQLModel):
    id: str
    property_id: str
    appraiser_id: str
    value: float
    report_url: str
    status: str
    created_at: datetime
    updated_at: datetime
    property: Property
    appraiser: User


class ManagementContractResponse(SQLModel):
    id: str
    property_id: str
    owner_id: str
    manager_id: str
    start_date: datetime
    end_date: datetime
    fee_percentage: float
    status: str
    created_at: datetime
    updated_at: datetime
    property: Property
    owner: User
    manager: User


class AdvisorySessionResponse(SQLModel):
    id: str
    client_id: str
    advisor_id: str
    topic: str
    notes: str
    status: str
    created_at: datetime
    updated_at: datetime
    client: User
    advisor: User
