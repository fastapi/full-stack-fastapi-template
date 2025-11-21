import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel
from .enums import *

# ============================================================================
# SHARED PROPERTIES (Legacy Support)
# ============================================================================

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class Message(SQLModel):
    message: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

# ============================================================================
# LEGACY MODELS (UUID-based - kept for backward compatibility)
# ============================================================================

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    images: list["Image"] = Relationship(back_populates="owner", cascade_delete=True)

class UserPublic(UserBase):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore

class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")

class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int

# ============================================================================
# IMAGE MODELS (Domain: Media Management)
# ============================================================================

class ImageBase(SQLModel):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    file_size: int
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    s3_bucket: str = Field(max_length=255)
    s3_key: str = Field(max_length=500)
    s3_url: str = Field(max_length=1000)
    processing_status: str = Field(
        default="pending",
        max_length=20,
        description="Processing status: pending, processing, completed, failed"
    )
    alt_text: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=500)

class ImageCreate(ImageBase):
    pass

class ImageUpdate(SQLModel):
    filename: str | None = Field(default=None, max_length=255)
    original_filename: str | None = Field(default=None, max_length=255)
    content_type: str | None = Field(default=None, max_length=100)
    file_size: int | None = Field(default=None)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    s3_bucket: str | None = Field(default=None, max_length=255)
    s3_key: str | None = Field(default=None, max_length=500)
    s3_url: str | None = Field(default=None, max_length=1000)
    processing_status: str | None = Field(default=None, max_length=20)
    alt_text: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=500)

class Image(ImageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)
    owner: User | None = Relationship(back_populates="images")
    variants: list["ImageVariant"] = Relationship(back_populates="image", cascade_delete=True)

class ImagePublic(ImageBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class ImagesPublic(SQLModel):
    data: list[ImagePublic]
    count: int

class ImageVariantBase(SQLModel):
    variant_type: str = Field(
        max_length=20,
        description="Variant type: large, medium, thumb"
    )
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    file_size: int
    s3_bucket: str = Field(max_length=255)
    s3_key: str = Field(max_length=500)
    s3_url: str = Field(max_length=1000)
    quality: int = Field(default=85)
    format: str = Field(default="jpeg", max_length=10)

class ImageVariant(ImageVariantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    image_id: uuid.UUID = Field(
        foreign_key="image.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    image: Image | None = Relationship(back_populates="variants")

class ImageVariantPublic(ImageVariantBase):
    id: uuid.UUID
    image_id: uuid.UUID

class ImageProcessingJobBase(SQLModel):
    status: str = Field(
        default="pending",
        max_length=20,
        description="Job status: pending, processing, completed, failed"
    )
    error_message: str | None = Field(default=None, max_length=1000)
    retry_count: int = Field(default=0)

class ImageProcessingJob(ImageProcessingJobBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    image_id: uuid.UUID = Field(
        foreign_key="image.id", nullable=False, ondelete="CASCADE"
    )
    image: Image | None = Relationship()

# ============================================================================
# LESMEE MODELS (INT + UUID Hybrid) - Schema only (no table=True for now)
# ============================================================================

# IDENTITY MODELS (Domain: User & Staff Management)

class UsersBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    user_type: UserRoleType = Field(default=UserRoleType.CUSTOMER)
    is_active: bool = True

class StaffBase(SQLModel):
    employee_code: Optional[str] = Field(default=None, max_length=50, unique=True)
    role: StaffRoleType
    department: Optional[str] = Field(default=None, max_length=100)
    skill_level: int = Field(default=1)
    is_available: bool = True

class StaffFinancesBase(SQLModel):
    base_salary: float = Field(default=0.0)
    bank_name: Optional[str] = Field(default=None, max_length=255)
    bank_account: Optional[str] = Field(default=None, max_length=50)
    tax_code: Optional[str] = Field(default=None, max_length=50)

class CustomerBase(SQLModel):
    customer_code: Optional[str] = Field(default=None, max_length=50, unique=True)
    company_name: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = None
    is_vip: bool = False
    sales_rep_id: Optional[int] = Field(default=None, foreign_key="staff.id")

# CATALOG MODELS (Domain: Product Management)

class ProductBase(SQLModel):
    name: str = Field(max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255, unique=True)
    base_price: float = Field(default=0.0)
    category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

class ProductOptionBase(SQLModel):
    option_name: str = Field(max_length=255)
    is_required: bool = False
    price_adjustment: float = Field(default=0.0)

# ORDER MODELS (Domain: Order Management)

class OrderBase(SQLModel):
    order_number: str = Field(max_length=50, unique=True)
    total_amount: float = Field(default=0.0)
    discount_amount: float = Field(default=0.0)
    paid_amount: float = Field(default=0.0)
    currency: str = Field(default="USD", max_length=3)
    status: OrderStatusType = Field(default=OrderStatusType.NEW)
    deadline_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    customer_note: Optional[str] = None
    internal_note: Optional[str] = None

class OrderItemBase(SQLModel):
    item_name: str = Field(max_length=255)
    quantity: int = Field(default=1)
    unit_price: float
    status: ItemStatusType = Field(default=ItemStatusType.PENDING)

class OrderAttachmentBase(SQLModel):
    file_name: str = Field(max_length=255)
    file_path: str
    file_type: FileTypeEnum

# FINANCIAL MODELS (Domain: Billing & Invoicing)

class InvoiceBase(SQLModel):
    invoice_number: Optional[str] = Field(default=None, max_length=50, unique=True)
    amount: float
    status: InvoiceStatusType = Field(default=InvoiceStatusType.DRAFT)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None

# WORKFLOW MODELS (Domain: Work Management)

class WorkAssignmentBase(SQLModel):
    work_type: WorkTypeEnum
    status: WorkStatusType = Field(default=WorkStatusType.ASSIGNED)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[float] = None
    staff_note: Optional[str] = None
    manager_note: Optional[str] = None

class CommissionBase(SQLModel):
    commission_type: CommissionTypeEnum
    amount: float
    percentage: Optional[float] = None
    is_paid: bool = False
    paid_date: Optional[datetime] = None

class WorkHistoryBase(SQLModel):
    action_type: str = Field(max_length=50)
    description: Optional[str] = None

class IssueBase(SQLModel):
    issue_type: Optional[str] = Field(default=None, max_length=50)
    severity: IssueSeverityType = Field(default=IssueSeverityType.MEDIUM)
    status: IssueStatusType = Field(default=IssueStatusType.OPEN)
    description: str
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

# CONFIGURATION MODELS (Domain: System Configuration)

class SettingBase(SQLModel):
    value: Optional[str] = None
    description: Optional[str] = None

class AuditLogBase(SQLModel):
    action_type: str = Field(max_length=50)
    table_name: Optional[str] = Field(default=None, max_length=100)
    record_id: Optional[str] = Field(default=None, max_length=50)
    ip_address: Optional[str] = Field(default=None, max_length=45)

# ============================================================================
# API SCHEMAS (Public Response Models)
# ============================================================================

# LESMEE API Schemas
class UsersCreate(UsersBase):
    password: str = Field(min_length=8, max_length=128)

class UsersUpdate(UsersBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    user_type: UserRoleType | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserPublicInt(UsersBase):
    id: int
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class UsersListPublic(SQLModel):
    data: list[UserPublicInt]
    count: int