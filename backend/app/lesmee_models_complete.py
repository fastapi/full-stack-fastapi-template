"""
Complete LESMEE Models with table implementations

This file contains the full LESMEE database models with proper table=True.
For development and migration testing, use this file.
For production use with existing legacy system, use models.py (base classes only).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel
from .enums import *

# ============================================================================
# IDENTITY MODELS (Domain: User & Staff Management)
# ============================================================================

class UsersBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    user_type: UserRoleType = Field(default=UserRoleType.CUSTOMER)
    is_active: bool = True

class Users(UsersBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    last_login_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    staff_profile: Optional["Staff"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    customer_profile: Optional["Customer"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})

class StaffBase(SQLModel):
    employee_code: Optional[str] = Field(default=None, max_length=50, unique=True)
    role: StaffRoleType
    department: Optional[str] = Field(default=None, max_length=100)
    skill_level: int = Field(default=1)
    is_available: bool = True

class Staff(StaffBase, table=True):
    __tablename__ = "staff"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Users = Relationship(back_populates="staff_profile")
    finances: Optional["StaffFinances"] = Relationship(back_populates="staff", sa_relationship_kwargs={"uselist": False})
    customer_assignments: List["Customer"] = Relationship(back_populates="sales_rep")

class StaffFinancesBase(SQLModel):
    base_salary: float = Field(default=0.0)
    bank_name: Optional[str] = Field(default=None, max_length=255)
    bank_account: Optional[str] = Field(default=None, max_length=50)
    tax_code: Optional[str] = Field(default=None, max_length=50)

class StaffFinances(StaffFinancesBase, table=True):
    __tablename__ = "staff_finances"

    staff_id: int = Field(foreign_key="staff.id", primary_key=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    staff: Staff = Relationship(back_populates="finances")

class CustomerBase(SQLModel):
    customer_code: Optional[str] = Field(default=None, max_length=50, unique=True)
    company_name: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = None
    is_vip: bool = False
    sales_rep_id: Optional[int] = Field(default=None, foreign_key="staff.id")

class Customer(CustomerBase, table=True):
    __tablename__ = "customers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Users = Relationship(back_populates="customer_profile")
    sales_rep: Optional[Staff] = Relationship(back_populates="customer_assignments")

# ============================================================================
# CATALOG MODELS (Domain: Product Management)
# ============================================================================

class ProductBase(SQLModel):
    name: str = Field(max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255, unique=True)
    base_price: float = Field(default=0.0)
    category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    commission_config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    product_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    options: List["ProductOption"] = Relationship(back_populates="product")
    orders: List["Order"] = Relationship(back_populates="product")

class ProductOptionBase(SQLModel):
    option_name: str = Field(max_length=255)
    is_required: bool = False
    price_adjustment: float = Field(default=0.0)

class ProductOption(ProductOptionBase, table=True):
    __tablename__ = "product_options"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    option_values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: Product = Relationship(back_populates="options")

# ============================================================================
# ORDER MODELS (Domain: Order Management)
# ============================================================================

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

class Order(OrderBase, table=True):
    __tablename__ = "orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id")
    product_id: int = Field(foreign_key="products.id")
    parent_order_id: Optional[uuid.UUID] = Field(foreign_key="orders.id")
    assigned_director_id: Optional[int] = Field(foreign_key="staff.id")
    assigned_saler_id: Optional[int] = Field(foreign_key="staff.id")
    ordered_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship()
    product: Product = Relationship(back_populates="orders")
    parent_order: Optional["Order"] = Relationship(
        back_populates="child_orders",
        sa_relationship_kwargs={"foreign_keys": "order.parent_order_id"}
    )
    child_orders: List["Order"] = Relationship(back_populates="parent_order")
    director: Optional[Staff] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "order.assigned_director_id"}
    )
    saler: Optional[Staff] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "order.assigned_saler_id"}
    )
    items: List["OrderItem"] = Relationship(back_populates="order")
    attachments: List["OrderAttachment"] = Relationship(back_populates="order")
    invoices: List["Invoice"] = Relationship(back_populates="order")
    commissions: List["Commission"] = Relationship(back_populates="order")

class OrderItemBase(SQLModel):
    item_name: str = Field(max_length=255)
    quantity: int = Field(default=1)
    unit_price: float
    status: ItemStatusType = Field(default=ItemStatusType.PENDING)

class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    assigned_staff_id: Optional[int] = Field(foreign_key="staff.id")
    specifications: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="items")
    assigned_staff: Optional[Staff] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "order_item.assigned_staff_id"}
    )
    work_assignments: List["WorkAssignment"] = Relationship(back_populates="order_item")
    issues: List["Issue"] = Relationship(back_populates="order_item")

class OrderAttachmentBase(SQLModel):
    file_name: str = Field(max_length=255)
    file_path: str
    file_type: FileTypeEnum

class OrderAttachment(OrderAttachmentBase, table=True):
    __tablename__ = "order_attachments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    uploaded_by: int = Field(foreign_key="users.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="attachments")

# ============================================================================
# FINANCIAL MODELS (Domain: Billing & Invoicing)
# ============================================================================

class InvoiceBase(SQLModel):
    invoice_number: Optional[str] = Field(default=None, max_length=50, unique=True)
    amount: float
    status: InvoiceStatusType = Field(default=InvoiceStatusType.DRAFT)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None

class Invoice(InvoiceBase, table=True):
    __tablename__ = "invoices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    commission_snapshot: dict = Field(default_factory=dict, sa_column=Column(JSON))
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="invoices")

# ============================================================================
# WORKFLOW MODELS (Domain: Work Management)
# ============================================================================

class WorkAssignmentBase(SQLModel):
    work_type: WorkTypeEnum
    status: WorkStatusType = Field(default=WorkStatusType.ASSIGNED)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[float] = None
    staff_note: Optional[str] = None
    manager_note: Optional[str] = None

class WorkAssignment(WorkAssignmentBase, table=True):
    __tablename__ = "work_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_item_id: int = Field(foreign_key="order_items.id")
    assigned_to: int = Field(foreign_key="staff.id")
    assigned_by: int = Field(foreign_key="users.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order_item: OrderItem = Relationship(back_populates="work_assignments")
    assigned_staff: Staff = Relationship(sa_relationship_kwargs={"foreign_keys": "work_assignment.assigned_to"})
    assigned_user: Users = Relationship(sa_relationship_kwargs={"foreign_keys": "work_assignment.assigned_by"})
    history: List["WorkHistory"] = Relationship(back_populates="assignment")

class CommissionBase(SQLModel):
    commission_type: CommissionTypeEnum
    amount: float
    percentage: Optional[float] = None
    is_paid: bool = False
    paid_date: Optional[datetime] = None

class Commission(CommissionBase, table=True):
    __tablename__ = "commissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="orders.id")
    staff_id: int = Field(foreign_key="staff.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="commissions")
    staff: Staff = Relationship()

class WorkHistoryBase(SQLModel):
    action_type: str = Field(max_length=50)
    description: Optional[str] = None

class WorkHistory(WorkHistoryBase, table=True):
    __tablename__ = "work_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: Optional[int] = Field(foreign_key="work_assignments.id")
    work_item_id: int = Field(foreign_key="order_items.id")
    action_by: int = Field(foreign_key="users.id")
    action_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assignment: Optional[WorkAssignment] = Relationship(back_populates="history")
    work_item: OrderItem = Relationship()
    action_user: Users = Relationship(sa_relationship_kwargs={"foreign_keys": "work_history.action_by"})

class IssueBase(SQLModel):
    issue_type: Optional[str] = Field(default=None, max_length=50)
    severity: IssueSeverityType = Field(default=IssueSeverityType.MEDIUM)
    status: IssueStatusType = Field(default=IssueStatusType.OPEN)
    description: str
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

class Issue(IssueBase, table=True):
    __tablename__ = "issues"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_item_id: int = Field(foreign_key="order_items.id")
    reported_by: int = Field(foreign_key="users.id")
    assigned_to: Optional[int] = Field(foreign_key="staff.id")
    resolved_by: Optional[int] = Field(foreign_key="staff.id")
    evidence_urls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order_item: OrderItem = Relationship(back_populates="issues")
    reported_user: Users = Relationship(sa_relationship_kwargs={"foreign_keys": "issue.reported_by"})
    assigned_staff: Optional[Staff] = Relationship(sa_relationship_kwargs={"foreign_keys": "issue.assigned_to"})
    resolver: Optional[Staff] = Relationship(sa_relationship_kwargs={"foreign_keys": "issue.resolved_by"})

# ============================================================================
# CONFIGURATION MODELS (Domain: System Configuration)
# ============================================================================

class SettingBase(SQLModel):
    value: Optional[str] = None
    description: Optional[str] = None

class Setting(SettingBase, table=True):
    __tablename__ = "settings"

    key: str = Field(primary_key=True, max_length=100)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLogBase(SQLModel):
    action_type: str = Field(max_length=50)
    table_name: Optional[str] = Field(default=None, max_length=100)
    record_id: Optional[str] = Field(default=None, max_length=50)
    ip_address: Optional[str] = Field(default=None, max_length=45)

class AuditLog(AuditLogBase, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    old_values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    action_user: Optional[Users] = Relationship(sa_relationship_kwargs={"foreign_keys": "audit_log.user_id"})

# ============================================================================
# API SCHEMAS (Public Response Models)
# ============================================================================

# Identity API Schemas
class UsersCreate(UsersBase):
    password: str = Field(min_length=8, max_length=128)

class UsersUpdate(UsersBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    user_type: UserRoleType | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UsersPublic(UsersBase):
    id: int
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class UsersListPublic(SQLModel):
    data: list[UsersPublic]
    count: int

# Staff API Schemas
class StaffCreate(StaffBase):
    user_id: int
    password: str = Field(min_length=8, max_length=128)

class StaffUpdate(StaffBase):
    user_id: int | None = None

class StaffPublic(StaffBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class StaffsPublic(SQLModel):
    data: list[StaffPublic]
    count: int

# Customer API Schemas
class CustomerCreate(CustomerBase):
    user_id: int
    password: str = Field(min_length=8, max_length=128)

class CustomerUpdate(CustomerBase):
    user_id: int | None = None

class CustomerPublic(CustomerBase):
    id: uuid.UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

class CustomersPublic(SQLModel):
    data: list[CustomerPublic]
    count: int

# Product API Schemas
class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductPublic(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int

# Order API Schemas
class OrderCreate(OrderBase):
    customer_id: uuid.UUID
    product_id: int

class OrderUpdate(OrderBase):
    parent_order_id: Optional[uuid.UUID] = None
    assigned_director_id: Optional[int] = None
    assigned_saler_id: Optional[int] = None

class OrderPublic(OrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    product_id: int
    ordered_at: datetime
    created_at: datetime
    updated_at: datetime

class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int

# Invoice API Schemas
class InvoiceCreate(InvoiceBase):
    order_id: uuid.UUID

class InvoiceUpdate(InvoiceBase):
    pass

class InvoicePublic(InvoiceBase):
    id: uuid.UUID
    order_id: uuid.UUID
    issue_date: datetime
    created_at: datetime
    updated_at: datetime

class InvoicesPublic(SQLModel):
    data: list[InvoicePublic]
    count: int

# Settings API Schemas
class SettingCreate(SettingBase):
    key: str = Field(max_length=100)

class SettingUpdate(SettingBase):
    pass

class SettingPublic(SettingBase):
    key: str
    updated_at: datetime

class SettingsPublic(SQLModel):
    data: list[SettingPublic]
    count: int

# Audit Log API Schemas
class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None

class AuditLogPublic(AuditLogBase):
    id: int
    user_id: Optional[int]
    old_values: Optional[dict]
    new_values: Optional[dict]
    created_at: datetime

class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int