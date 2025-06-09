import uuid
from typing import Optional, List, Dict, Any
from pydantic import EmailStr, Field, HttpUrl
from sqlmodel import Relationship, SQLModel
from datetime import datetime
from enum import Enum
from decimal import Decimal


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


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    phone: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


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
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    owner: User | None = Relationship(back_populates="items")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


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
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreate(SQLModel):
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(SQLModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
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


# Credit Models