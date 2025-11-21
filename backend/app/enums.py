from enum import Enum
from sqlmodel import SQLModel

class UserRoleType(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class StaffRoleType(str, Enum):
    EDITOR = "editor"
    QA = "qa"
    SALER = "saler"
    DIRECTOR = "director"
    MANAGER = "manager"
    ADMIN = "admin"

class OrderStatusType(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ItemStatusType(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class WorkTypeEnum(str, Enum):
    EDITING = "editing"
    QA = "qa"
    REVIEW = "review"
    CORRECTION = "correction"

class WorkStatusType(str, Enum):
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class InvoiceStatusType(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class CommissionTypeEnum(str, Enum):
    SALER_BONUS = "saler_bonus"
    DIRECTOR_FEE = "director_fee"
    EDITOR_PAYMENT = "editor_payment"
    QA_FEE = "qa_fee"

class IssueSeverityType(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueStatusType(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class FileTypeEnum(str, Enum):
    CUSTOMER_INPUT = "customer_input"
    DELIVERABLE = "deliverable"
    REFERENCE = "reference"