import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, Text
from typing import List, Optional, Dict, Any
from pydantic import EmailStr, HttpUrl
from decimal import Decimal
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# User and Item models defined below in this file
# UserRole enum defined below

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


# 👥 TABLA USUARIOS - TABLA REAL
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    clerk_id: Optional[str] = Field(default=None, unique=True, index=True)
    hashed_password: str = Field(sa_column=Column(Text))
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    items: List["Item"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


# 📦 TABLA ITEMS - TABLA REAL
class Item(SQLModel, table=True):
    __tablename__ = "items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    owner: Optional[User] = Relationship(back_populates="items")


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: str = "user"


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


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: List[UserPublic]
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


class PropertyBase(SQLModel):
    title: str
    description: str
    property_type: str  # casa, apartamento, local, terreno
    status: str  # disponible, reservado, vendido, alquilado
    price: float
    currency: str = "USD"
    address: str
    city: str
    state: str
    country: str
    zip_code: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: float  # en metros cuadrados
    features: List[str] = []
    amenities: List[str] = []
    images: List[HttpUrl] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    year_built: Optional[int] = None
    condition: Optional[str] = None
    parking_spaces: Optional[int] = None
    agent_id: uuid.UUID
    owner_id: uuid.UUID


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    features: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[HttpUrl]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    year_built: Optional[int] = None
    condition: Optional[str] = None
    parking_spaces: Optional[int] = None


class Property(PropertyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    views: int = 0
    favorites: int = 0
    visits: int = 0

    class Config:
        from_attributes = True


class PropertySearch(SQLModel):
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    max_bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    features: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    status: Optional[str] = None


class PropertyVisit(SQLModel):
    property_id: uuid.UUID
    client_id: uuid.UUID
    visit_date: datetime
    status: str  # programada, completada, cancelada
    notes: Optional[str] = None
    agent_id: uuid.UUID
    feedback: Optional[Dict[str, Any]] = None


class PropertyVisitCreate(SQLModel):
    property_id: uuid.UUID
    client_id: uuid.UUID
    visit_date: datetime
    notes: Optional[str] = None
    agent_id: uuid.UUID


class PropertyVisitUpdate(SQLModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None


class PropertyFavorite(SQLModel):
    property_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


class PropertyView(SQLModel):
    property_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    ip_address: str
    user_agent: str
    created_at: datetime


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


class AuditLog(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    audit_metadata: Optional[Dict[str, Any]] = None  # Renamed to avoid shadow warning
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreate(SQLModel):
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    audit_metadata: Optional[Dict[str, Any]] = None  # Renamed to avoid shadow warning
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(SQLModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    audit_metadata: Optional[Dict[str, Any]] = None  # Renamed to avoid shadow warning
    created_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class MarketAnalysisBase(SQLModel):
    property_type: str
    location: str
    period: str  # monthly, quarterly, yearly
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, Any]  # Precios promedio, tendencias, etc.
    insights: List[str]
    recommendations: List[str]


class MarketAnalysisCreate(MarketAnalysisBase):
    pass


class MarketAnalysisUpdate(SQLModel):
    metrics: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None


class MarketAnalysis(SQLModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID


class AgentPerformanceBase(SQLModel):
    agent_id: uuid.UUID
    period: str  # monthly, quarterly, yearly
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, Any]  # Ventas, visitas, conversiones, etc.
    goals: Dict[str, Any]
    achievements: List[str]


class AgentPerformanceCreate(AgentPerformanceBase):
    pass


class AgentPerformanceUpdate(SQLModel):
    metrics: Optional[Dict[str, Any]] = None
    goals: Optional[Dict[str, Any]] = None
    achievements: Optional[List[str]] = None


class AgentPerformance(SQLModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FinancialReportBase(SQLModel):
    report_type: str  # income, expenses, commissions, etc.
    period: str  # monthly, quarterly, yearly
    start_date: datetime
    end_date: datetime
    data: Dict[str, Any]  # Ingresos, gastos, comisiones, etc.
    summary: Dict[str, Any]
    analysis: List[str]


class FinancialReportCreate(FinancialReportBase):
    pass


class FinancialReportUpdate(SQLModel):
    data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    analysis: Optional[List[str]] = None


class FinancialReport(SQLModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID


class DashboardMetricsBase(SQLModel):
    dashboard_type: str  # ceo, manager, supervisor, agent
    period: str  # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    alerts: List[Dict[str, Any]]


class DashboardMetricsCreate(DashboardMetricsBase):
    pass


class DashboardMetricsUpdate(SQLModel):
    metrics: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, Any]] = None
    alerts: Optional[List[Dict[str, Any]]] = None


class DashboardMetrics(SQLModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_updated: datetime


# Financial Analysis Models
class CreditScoreBase(SQLModel):
    client_id: str
    score: int
    factors: Dict[str, float]
    risk_level: str
    last_updated: datetime
    valid_until: datetime
    notes: Optional[str] = None


class CreditScoreCreate(CreditScoreBase):
    pass


class CreditScoreUpdate(SQLModel):
    score: Optional[int] = None
    factors: Optional[Dict[str, float]] = None
    risk_level: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class CreditScore(CreditScoreBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str


class CreditHistoryBase(SQLModel):
    client_id: str
    loan_id: str
    payment_status: str
    delinquency_days: int
    payment_history: List[Dict[str, Any]]
    credit_utilization: float
    credit_limit: float
    notes: Optional[str] = None


class CreditHistoryCreate(CreditHistoryBase):
    pass


class CreditHistoryUpdate(SQLModel):
    payment_status: Optional[str] = None
    delinquency_days: Optional[int] = None
    payment_history: Optional[List[Dict[str, Any]]] = None
    credit_utilization: Optional[float] = None
    notes: Optional[str] = None


class CreditHistory(CreditHistoryBase):
    id: str
    created_at: datetime
    updated_at: datetime


class FinancialReportBase(SQLModel):
    report_type: str  # portfolio, risk, profitability, etc.
    period: str
    start_date: datetime
    end_date: datetime
    data: Dict[str, Any]
    summary: Dict[str, Any]
    analysis: Dict[str, Any]
    recommendations: List[str]
    notes: Optional[str] = None


class FinancialReportCreate(FinancialReportBase):
    pass


class FinancialReportUpdate(SQLModel):
    data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    notes: Optional[str] = None


class FinancialReport(FinancialReportBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str


class RiskAnalysisBase(SQLModel):
    loan_id: str
    risk_score: float
    risk_factors: Dict[str, float]
    risk_level: str
    mitigation_measures: List[str]
    monitoring_plan: Dict[str, Any]
    notes: Optional[str] = None


class RiskAnalysisCreate(RiskAnalysisBase):
    pass


class RiskAnalysisUpdate(SQLModel):
    risk_score: Optional[float] = None
    risk_factors: Optional[Dict[str, float]] = None
    risk_level: Optional[str] = None
    mitigation_measures: Optional[List[str]] = None
    monitoring_plan: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class RiskAnalysis(RiskAnalysisBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    last_reviewed: Optional[datetime] = None
    reviewed_by: Optional[str] = None


class MortgageLoanBase(SQLModel):
    property_id: str
    loan_amount: Decimal
    interest_rate: Decimal
    term_years: int
    ltv_ratio: Decimal  # Loan to Value ratio
    monthly_payment: Decimal
    insurance_required: bool
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_coverage: Optional[Decimal] = None
    appraisal_value: Decimal
    appraisal_date: datetime
    appraisal_company: str
    legal_documents: List[str]  # Lista de IDs de documentos legales
    status: str = "pending"  # pending, approved, rejected, active, completed, defaulted


class MortgageLoanCreate(MortgageLoanBase):
    pass


class MortgageLoanUpdate(SQLModel):
    status: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_coverage: Optional[Decimal] = None
    legal_documents: Optional[List[str]] = None


class MortgageLoan(MortgageLoanBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None


class InvestmentLoanBase(SQLModel):
    project_id: str
    loan_amount: Decimal
    interest_rate: Decimal
    term_years: int
    expected_roi: Decimal
    business_plan: str  # ID del documento del plan de negocio
    collateral_type: str  # Tipo de garantía
    collateral_value: Decimal
    collateral_documents: List[str]  # Lista de IDs de documentos de garantía
    risk_assessment: Dict[str, Any]  # Evaluación de riesgo
    status: str = "pending"  # pending, approved, rejected, active, completed, defaulted


class InvestmentLoanCreate(InvestmentLoanBase):
    pass


class InvestmentLoanUpdate(SQLModel):
    status: Optional[str] = None
    expected_roi: Optional[Decimal] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    collateral_documents: Optional[List[str]] = None


class InvestmentLoan(InvestmentLoanBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None


# Legal Compliance System Models
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

class LegalDocumentTemplate(SQLModel):
    id: Optional[uuid.UUID] = None
    template_name: str
    document_type: LegalDocumentType
    version: str
    content: str  # HTML content with placeholders
    variables: Dict[str, Any]  # Template variables definition
    is_active: bool = True
    created_by: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LegalDocumentTemplateCreate(SQLModel):
    template_name: str
    document_type: LegalDocumentType
    version: str
    content: str
    variables: Dict[str, Any]
    created_by: uuid.UUID

class LegalDocumentTemplateUpdate(SQLModel):
    template_name: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class GeneratedLegalDocument(SQLModel):
    id: Optional[uuid.UUID] = None
    template_id: uuid.UUID
    document_number: str  # Auto-generated unique number
    document_type: LegalDocumentType
    title: str
    content: str  # Generated HTML content
    variables_used: Dict[str, Any]  # Values used for generation
    status: LegalDocumentStatus = LegalDocumentStatus.DRAFT
    client_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None
    loan_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    generated_by: uuid.UUID
    signed_by_client: Optional[bool] = False
    signed_by_agent: Optional[bool] = False
    signature_client_date: Optional[datetime] = None
    signature_agent_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class GeneratedLegalDocumentCreate(SQLModel):
    template_id: uuid.UUID
    title: str
    variables_used: Dict[str, Any]
    client_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None
    loan_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    generated_by: uuid.UUID

class GeneratedLegalDocumentUpdate(SQLModel):
    title: Optional[str] = None
    status: Optional[LegalDocumentStatus] = None
    signed_by_client: Optional[bool] = None
    signed_by_agent: Optional[bool] = None

class ComplianceAudit(SQLModel):
    id: Optional[uuid.UUID] = None
    audit_type: str  # "document_review", "process_compliance", "data_protection"
    entity_type: str  # "contract", "loan", "property", "user"
    entity_id: uuid.UUID
    compliance_status: str  # "compliant", "non_compliant", "pending_review"
    findings: List[str]
    recommendations: List[str]
    auditor_id: uuid.UUID
    audit_date: datetime
    next_audit_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

class ComplianceAuditCreate(SQLModel):
    audit_type: str
    entity_type: str
    entity_id: uuid.UUID
    compliance_status: str
    findings: List[str]
    recommendations: List[str]
    auditor_id: uuid.UUID
    next_audit_date: Optional[datetime] = None

class DataProtectionConsent(SQLModel):
    id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    consent_type: str  # "data_processing", "marketing", "third_party_sharing"
    consent_given: bool
    consent_date: datetime
    consent_version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    withdrawn_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

class DataProtectionConsentCreate(SQLModel):
    user_id: uuid.UUID
    consent_type: str
    consent_given: bool
    consent_version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Credit Models