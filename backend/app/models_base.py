"""
🏗️ MODELOS BASE PARA RAILWAY POSTGRESQL
SQLModel models que funcionan como tablas reales
"""

import uuid
from typing import Optional, List, Dict, Any
from pydantic import EmailStr, Field, HttpUrl
from sqlmodel import Relationship, SQLModel, Column, String, Text, Integer, Boolean, DateTime, Numeric, ARRAY
from datetime import datetime
from enum import Enum
from decimal import Decimal
import sqlalchemy as sa


# 🎯 ENUMS
class UserRole(str, Enum):
    CEO = "ceo"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    HR = "hr"
    SUPPORT = "support"
    AGENT = "agent"
    CLIENT = "client"
    USER = "user"


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


class VisitStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LegalDocumentType(str, Enum):
    SALE_CONTRACT = "sale_contract"
    RENTAL_CONTRACT = "rental_contract"
    LOAN_CONTRACT = "loan_contract"
    INTERMEDIATION_CONTRACT = "intermediation_contract"
    PRIVACY_POLICY = "privacy_policy"
    TERMS_CONDITIONS = "terms_conditions"
    MORTGAGE_CONTRACT = "mortgage_contract"
    PROMISSORY_NOTE = "promissory_note"


class LegalDocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"


# 👥 TABLA USUARIOS - TABLA REAL
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(sa_column=Column(Text))
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    items: List["Item"] = Relationship(back_populates="owner")
    properties_owned: List["Property"] = Relationship(back_populates="owner", sa_relationship_kwargs={"foreign_keys": "Property.owner_id"})
    properties_managed: List["Property"] = Relationship(back_populates="agent", sa_relationship_kwargs={"foreign_keys": "Property.agent_id"})


# 📦 TABLA ITEMS - TABLA REAL
class Item(SQLModel, table=True):
    __tablename__ = "items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    owner_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    owner: Optional[User] = Relationship(back_populates="items")


# 🏠 TABLA PROPIEDADES - TABLA REAL
class Property(SQLModel, table=True):
    __tablename__ = "properties"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    property_type: PropertyType
    status: PropertyStatus = Field(default=PropertyStatus.AVAILABLE)
    price: Decimal = Field(sa_column=Column(Numeric(15, 2)))
    currency: str = Field(default="USD", max_length=3)
    address: str = Field(sa_column=Column(Text))
    city: str = Field(max_length=100)
    state: str = Field(max_length=100)
    country: str = Field(max_length=100)
    zip_code: Optional[str] = Field(default=None, max_length=20)
    bedrooms: Optional[int] = Field(default=None)
    bathrooms: Optional[int] = Field(default=None)
    area: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    features: Optional[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(sa.dialects.postgresql.JSONB))
    amenities: Optional[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(sa.dialects.postgresql.JSONB))
    images: Optional[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(sa.dialects.postgresql.JSONB))
    latitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    longitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(11, 8)))
    year_built: Optional[int] = Field(default=None)
    condition: Optional[str] = Field(default=None, max_length=50)
    parking_spaces: int = Field(default=0)
    views: int = Field(default=0)
    favorites: int = Field(default=0)
    visits: int = Field(default=0)
    agent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    agent: Optional[User] = Relationship(back_populates="properties_managed", sa_relationship_kwargs={"foreign_keys": "Property.agent_id"})
    owner: Optional[User] = Relationship(back_populates="properties_owned", sa_relationship_kwargs={"foreign_keys": "Property.owner_id"})


# 👁️ TABLA VISTAS PROPIEDADES - TABLA REAL
class PropertyView(SQLModel, table=True):
    __tablename__ = "property_views"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ❤️ TABLA FAVORITOS - TABLA REAL
class PropertyFavorite(SQLModel, table=True):
    __tablename__ = "property_favorites"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# 🏠 TABLA VISITAS - TABLA REAL
class PropertyVisit(SQLModel, table=True):
    __tablename__ = "property_visits"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    client_id: uuid.UUID = Field(foreign_key="users.id")
    agent_id: uuid.UUID = Field(foreign_key="users.id")
    visit_date: datetime
    status: VisitStatus = Field(default=VisitStatus.SCHEDULED)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    feedback: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(sa.dialects.postgresql.JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# 📝 TABLA AUDITORÍA - TABLA REAL
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)
    entity_type: str = Field(max_length=50)
    entity_id: uuid.UUID
    changes: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(sa.dialects.postgresql.JSONB))
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(sa.dialects.postgresql.JSONB))
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow) 