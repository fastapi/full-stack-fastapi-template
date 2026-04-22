import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import EmailStr
from sqlalchemy import JSON, Column, DateTime, Text
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Enum for predefined roles
class RoleEnum(str, Enum):
    ADMIN = "admin"
    RUNNER = "runner"
    ORGANIZER = "organizer"
    VOLUNTEER = "volunteer"


# Enum for race status
class RaceStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Enum for registration status
class RegistrationStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLIST = "waitlist"


# Enum for payment status
class PaymentStatusEnum(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIAL = "partial"


# Enum for race result status
class ResultStatusEnum(str, Enum):
    FINISHED = "finished"
    DNF = "dnf"  # Did Not Finish
    DNS = "dns"  # Did Not Start
    DQ = "dq"  # Disqualified


# Enum for flexible attribute types
class AttributeTypeEnum(str, Enum):
    STRING = "string"
    TEXT = "text"
    URL = "url"
    DATE = "date"
    DATETIME = "datetime"
    NUMBER = "number"
    BOOLEAN = "boolean"
    EMAIL = "email"
    PHONE = "phone"


class TerrainEnum(str, Enum):
    ROAD = "road"
    TRAIL = "trail"
    TRACK = "track"
    MIXED = "mixed"


class DifficultyEnum(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    EXTREME = "extreme"


class FitnessEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class DistancePrefEnum(str, Enum):
    SHORT = "short"   # 5K and under
    MID = "mid"       # 10K–half marathon
    LONG = "long"     # full marathon
    ULTRA = "ultra"   # 50K+


class InteractionTypeEnum(str, Enum):
    VIEWED = "viewed"
    SAVED = "saved"
    UNSAVED = "unsaved"
    REGISTERED = "registered"
    SHARED = "shared"


# Link table for many-to-many relationship between User and Role
class UserRoleLink(SQLModel, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True, ondelete="CASCADE"
    )


# Role model
class RoleBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class Role(RoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True)),
    )
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)


class RolePublic(RoleBase):
    id: uuid.UUID
    created_at: datetime | None = None


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


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
    email: EmailStr | None = Field(default=None, max_length=255)
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
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True)),
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    roles: list[Role] = Relationship(back_populates="users", link_model=UserRoleLink)
    # Race relationships
    organized_races: list["Race"] = Relationship(
        back_populates="organizer", cascade_delete=True
    )
    race_registrations: list["RaceRegistration"] = Relationship(
        back_populates="runner", cascade_delete=True
    )
    profile: Optional["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False},
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    roles: list[RolePublic] = []


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
    title: str | None = Field(default=None, min_length=1, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True)),
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# =============================================================================
# MediaAsset - Reusable media for any content type (race, article, etc.)
# =============================================================================


class MediaAssetBase(SQLModel):
    content_type: str = Field(max_length=100, index=True)
    content_id: uuid.UUID = Field(index=True)
    kind: str = Field(default="gallery", max_length=50, index=True)

    alt_text: str | None = Field(default=None, max_length=255)
    display_order: int = Field(default=0)
    is_primary: bool = False
    is_public: bool = True


class MediaAssetCreate(MediaAssetBase):
    original_filename: str = Field(max_length=255)
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=1000)
    file_url: str = Field(max_length=1000)
    mime_type: str = Field(max_length=100)
    size_bytes: int = Field(ge=0)
    uploaded_by_id: uuid.UUID | None = None


class MediaAssetUpdate(SQLModel):
    kind: str | None = Field(default=None, max_length=50)
    alt_text: str | None = Field(default=None, max_length=255)
    display_order: int | None = None
    is_primary: bool | None = None
    is_public: bool | None = None


class MediaAsset(MediaAssetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    original_filename: str = Field(max_length=255)
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=1000)
    file_url: str = Field(max_length=1000)
    mime_type: str = Field(max_length=100)
    size_bytes: int = Field(ge=0)
    uploaded_by_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )


class MediaAssetPublic(MediaAssetBase):
    id: uuid.UUID
    original_filename: str
    file_name: str
    file_url: str
    mime_type: str
    size_bytes: int
    uploaded_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class MediaAssetsPublic(SQLModel):
    data: list[MediaAssetPublic]
    count: int


# =============================================================================
# Race Models
# =============================================================================


# Junction table for many-to-many Race ↔ RaceTag
class RaceTagLink(SQLModel, table=True):
    race_id: uuid.UUID = Field(
        foreign_key="race.id", primary_key=True, ondelete="CASCADE"
    )
    tag_id: uuid.UUID = Field(
        foreign_key="racetag.id", primary_key=True, ondelete="CASCADE"
    )


class RaceTagBase(SQLModel):
    name: str = Field(max_length=50, unique=True, index=True)
    slug: str = Field(max_length=50, unique=True, index=True)


class RaceTagCreate(RaceTagBase):
    pass


class RaceTag(RaceTagBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    races: list["Race"] = Relationship(
        back_populates="tags", link_model=RaceTagLink
    )


class TagPublic(RaceTagBase):
    id: uuid.UUID


class TagsPublic(SQLModel):
    data: list[TagPublic]
    count: int


# Race - Main race event
class RaceBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=2000)

    # Overall event period (for multi-day events)
    event_start_date: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    event_end_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Location
    location: str = Field(max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="USA", max_length=100)

    # Overall registration (can be overridden per category)
    registration_start: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    registration_end: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Status
    status: RaceStatusEnum = Field(default=RaceStatusEnum.DRAFT)
    is_active: bool = True

    # Default pricing (can be overridden per category)
    base_price: float | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", max_length=3)

    # Flexible metadata stored as JSON
    race_metadata: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    # Geographic coordinates
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    # Course characteristics
    terrain_type: TerrainEnum | None = Field(default=None)
    difficulty_level: DifficultyEnum | None = Field(default=None)
    elevation_gain_m: int | None = Field(default=None, ge=0)
    is_certified: bool = Field(default=False)
    gpx_file_url: str | None = Field(default=None, max_length=1000)
    website_url: str | None = Field(default=None, max_length=1000)


class RaceCreate(RaceBase):
    pass


class RaceUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    event_start_date: datetime | None = None
    event_end_date: datetime | None = None
    location: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    registration_start: datetime | None = None
    registration_end: datetime | None = None
    status: RaceStatusEnum | None = None
    is_active: bool | None = None
    base_price: float | None = None
    currency: str | None = None
    race_metadata: dict[str, Any] | None = None
    latitude: float | None = None
    longitude: float | None = None
    terrain_type: TerrainEnum | None = None
    difficulty_level: DifficultyEnum | None = None
    elevation_gain_m: int | None = None
    is_certified: bool | None = None
    gpx_file_url: str | None = None
    website_url: str | None = None
    tag_ids: list[uuid.UUID] | None = None


class Race(RaceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Foreign keys
    organizer_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    # Relationships
    organizer: User = Relationship(back_populates="organized_races")
    categories: list["RaceCategory"] = Relationship(
        back_populates="race", cascade_delete=True
    )
    registrations: list["RaceRegistration"] = Relationship(
        back_populates="race", cascade_delete=True
    )
    attributes: list["RaceAttribute"] = Relationship(
        back_populates="race", cascade_delete=True
    )
    checkpoints: list["RaceCheckpoint"] = Relationship(
        back_populates="race", cascade_delete=True
    )
    tags: list[RaceTag] = Relationship(
        back_populates="races", link_model=RaceTagLink
    )


class RacePublic(RaceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    organizer_id: uuid.UUID


class RacePublicWithDetails(RacePublic):
    categories: list["RaceCategoryPublic"] = []
    tags: list[TagPublic] = []
    registration_count: int = 0


class RacePublicWithDistance(RacePublic):
    distance_km: float


class RacesPublic(SQLModel):
    data: list[RacePublic]
    count: int


class RacesPublicWithDistance(SQLModel):
    data: list[RacePublicWithDistance]
    count: int


# RaceCategory - Distance/Type variations
class RaceCategoryBase(SQLModel):
    name: str = Field(max_length=100)
    distance_km: float = Field(gt=0)
    distance_unit: str = Field(default="km", max_length=10)

    # Category-specific start and end times
    start_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    end_time: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Time limits
    cutoff_time_minutes: int | None = Field(default=None, ge=0)

    # Category-specific registration window (overrides race defaults)
    registration_start: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    registration_end: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Category-specific pricing
    price: float | None = Field(default=None, ge=0)
    early_bird_price: float | None = Field(default=None, ge=0)
    early_bird_deadline: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Capacity
    max_participants: int | None = Field(default=None, ge=1)

    # Age/gender restrictions
    min_age: int | None = Field(default=None, ge=0)
    max_age: int | None = Field(default=None, ge=0)
    gender_restriction: str | None = Field(default=None, max_length=20)

    # Display
    description: str | None = Field(default=None, max_length=500)
    display_order: int = Field(default=0)
    is_active: bool = True


class RaceCategoryCreate(RaceCategoryBase):
    race_id: uuid.UUID


class RaceCategoryUpdate(SQLModel):
    name: str | None = None
    distance_km: float | None = None
    distance_unit: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    cutoff_time_minutes: int | None = None
    registration_start: datetime | None = None
    registration_end: datetime | None = None
    price: float | None = None
    early_bird_price: float | None = None
    early_bird_deadline: datetime | None = None
    max_participants: int | None = None
    min_age: int | None = None
    max_age: int | None = None
    gender_restriction: str | None = None
    description: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


class RaceCategory(RaceCategoryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(
        foreign_key="race.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    race: Race = Relationship(back_populates="categories")
    registrations: list["RaceRegistration"] = Relationship(
        back_populates="category", cascade_delete=True
    )


class RaceCategoryPublic(RaceCategoryBase):
    id: uuid.UUID
    race_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RaceCategoryPublicWithDetails(RaceCategoryPublic):
    registration_count: int = 0
    available_spots: int | None = None
    is_registration_open: bool = False
    current_price: float | None = None


class RaceCategoriesPublic(SQLModel):
    data: list[RaceCategoryPublic]
    count: int


# RaceRegistration - Runner registrations
class RaceRegistrationBase(SQLModel):
    # Runner information
    bib_number: str | None = Field(default=None, max_length=50)
    emergency_contact: str | None = Field(default=None, max_length=255)
    emergency_phone: str | None = Field(default=None, max_length=50)

    # Additional info
    tshirt_size: str | None = Field(default=None, max_length=10)
    special_requirements: str | None = Field(default=None, max_length=500)

    # Payment & status
    registration_status: RegistrationStatusEnum = Field(
        default=RegistrationStatusEnum.PENDING
    )
    payment_status: PaymentStatusEnum = Field(default=PaymentStatusEnum.UNPAID)
    amount_paid: float | None = Field(default=None, ge=0)
    payment_reference: str | None = Field(default=None, max_length=255)

    # Extra data stored as JSON
    registration_data: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON)
    )


class RaceRegistrationCreate(RaceRegistrationBase):
    race_id: uuid.UUID
    category_id: uuid.UUID


class RaceRegistrationUpdate(SQLModel):
    bib_number: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    tshirt_size: str | None = None
    special_requirements: str | None = None
    registration_status: RegistrationStatusEnum | None = None
    payment_status: PaymentStatusEnum | None = None
    amount_paid: float | None = None
    payment_reference: str | None = None
    registration_data: dict[str, Any] | None = None


class RaceRegistration(RaceRegistrationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(
        foreign_key="race.id", nullable=False, ondelete="CASCADE"
    )
    category_id: uuid.UUID = Field(
        foreign_key="racecategory.id", nullable=False, ondelete="CASCADE"
    )
    runner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    registered_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    race: Race = Relationship(back_populates="registrations")
    category: RaceCategory = Relationship(back_populates="registrations")
    runner: User = Relationship(back_populates="race_registrations")
    result: Optional["RaceResult"] = Relationship(
        back_populates="registration", sa_relationship_kwargs={"uselist": False}
    )
    split_times: list["RaceSplitTime"] = Relationship(
        back_populates="registration", cascade_delete=True
    )


class RaceRegistrationPublic(RaceRegistrationBase):
    id: uuid.UUID
    race_id: uuid.UUID
    category_id: uuid.UUID
    runner_id: uuid.UUID
    registered_at: datetime
    updated_at: datetime


class RaceRegistrationPublicWithDetails(RaceRegistrationPublic):
    runner: UserPublic
    category: RaceCategoryPublic


class RaceRegistrationsPublic(SQLModel):
    data: list[RaceRegistrationPublic]
    count: int


# RaceResult - Race completion results
class RaceResultBase(SQLModel):
    finish_time_seconds: int | None = Field(default=None, ge=0)
    overall_position: int | None = Field(default=None, ge=1)
    category_position: int | None = Field(default=None, ge=1)
    gender_position: int | None = Field(default=None, ge=1)

    status: ResultStatusEnum = Field(default=ResultStatusEnum.FINISHED)

    # Calculated fields
    pace_per_km_seconds: float | None = None
    notes: str | None = Field(default=None, max_length=500)


class RaceResultCreate(RaceResultBase):
    registration_id: uuid.UUID


class RaceResultUpdate(RaceResultBase):
    finish_time_seconds: int | None = None
    overall_position: int | None = None
    category_position: int | None = None
    gender_position: int | None = None
    status: ResultStatusEnum | None = None
    pace_per_km_seconds: float | None = None
    notes: str | None = None


class RaceResult(RaceResultBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    registration_id: uuid.UUID = Field(
        foreign_key="raceregistration.id",
        unique=True,
        nullable=False,
        ondelete="CASCADE",
    )

    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    registration: RaceRegistration = Relationship(back_populates="result")


class RaceResultPublic(RaceResultBase):
    id: uuid.UUID
    registration_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RaceResultsPublic(SQLModel):
    data: list[RaceResultPublic]
    count: int


# RaceAttribute - Flexible key-value attributes
class RaceAttributeBase(SQLModel):
    key: str = Field(max_length=100, index=True)
    value_text: str | None = Field(default=None, sa_column=Column(Text))

    # Metadata about the attribute
    attribute_type: AttributeTypeEnum = Field(default=AttributeTypeEnum.STRING)
    label: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_required: bool = False
    is_public: bool = True
    display_order: int = Field(default=0)


class RaceAttributeCreate(RaceAttributeBase):
    race_id: uuid.UUID


class RaceAttributeUpdate(SQLModel):
    value_text: str | None = None
    attribute_type: AttributeTypeEnum | None = None
    label: str | None = None
    description: str | None = None
    is_required: bool | None = None
    is_public: bool | None = None
    display_order: int | None = None


class RaceAttribute(RaceAttributeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(
        foreign_key="race.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    race: Race = Relationship(back_populates="attributes")


class RaceAttributePublic(RaceAttributeBase):
    id: uuid.UUID
    race_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RaceAttributesPublic(SQLModel):
    data: list[RaceAttributePublic]
    count: int


# RaceCheckpoint - For split times tracking
class RaceCheckpointBase(SQLModel):
    name: str = Field(max_length=100)
    distance_km: float = Field(ge=0)
    sequence: int = Field(ge=1)
    is_active: bool = True


class RaceCheckpointCreate(RaceCheckpointBase):
    race_id: uuid.UUID


class RaceCheckpointUpdate(SQLModel):
    name: str | None = None
    distance_km: float | None = None
    sequence: int | None = None
    is_active: bool | None = None


class RaceCheckpoint(RaceCheckpointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(
        foreign_key="race.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    race: Race = Relationship(back_populates="checkpoints")
    split_times: list["RaceSplitTime"] = Relationship(
        back_populates="checkpoint", cascade_delete=True
    )


class RaceCheckpointPublic(RaceCheckpointBase):
    id: uuid.UUID
    race_id: uuid.UUID
    created_at: datetime


class RaceCheckpointsPublic(SQLModel):
    data: list[RaceCheckpointPublic]
    count: int


# RaceSplitTime - Split times at checkpoints
class RaceSplitTimeBase(SQLModel):
    time_seconds: int = Field(ge=0)


class RaceSplitTimeCreate(RaceSplitTimeBase):
    registration_id: uuid.UUID
    checkpoint_id: uuid.UUID


class RaceSplitTimeUpdate(SQLModel):
    time_seconds: int | None = None


class RaceSplitTime(RaceSplitTimeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    registration_id: uuid.UUID = Field(
        foreign_key="raceregistration.id", nullable=False, ondelete="CASCADE"
    )
    checkpoint_id: uuid.UUID = Field(
        foreign_key="racecheckpoint.id", nullable=False, ondelete="CASCADE"
    )
    recorded_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    registration: RaceRegistration = Relationship(back_populates="split_times")
    checkpoint: RaceCheckpoint = Relationship(back_populates="split_times")


class RaceSplitTimePublic(RaceSplitTimeBase):
    id: uuid.UUID
    registration_id: uuid.UUID
    checkpoint_id: uuid.UUID
    recorded_at: datetime


class RaceSplitTimesPublic(SQLModel):
    data: list[RaceSplitTimePublic]
    count: int


# =============================================================================
# End of Race Models
# =============================================================================


# =============================================================================
# UserProfile - Runner preferences and personalization data
# =============================================================================


class UserProfileBase(SQLModel):
    fitness_level: FitnessEnum | None = None
    distance_preference: DistancePrefEnum | None = None
    terrain_preference: TerrainEnum | None = None
    home_latitude: float | None = Field(default=None, ge=-90, le=90)
    home_longitude: float | None = Field(default=None, ge=-180, le=180)
    home_city: str | None = Field(default=None, max_length=100)
    weekly_mileage_km: float | None = Field(default=None, ge=0)
    goal_race_date: date | None = None
    bio: str | None = Field(default=None, sa_column=Column(Text))
    is_onboarded: bool = Field(default=False)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(SQLModel):
    fitness_level: FitnessEnum | None = None
    distance_preference: DistancePrefEnum | None = None
    terrain_preference: TerrainEnum | None = None
    home_latitude: float | None = None
    home_longitude: float | None = None
    home_city: str | None = None
    weekly_mileage_km: float | None = None
    goal_race_date: date | None = None
    bio: str | None = None
    is_onboarded: bool | None = None


class UserProfile(UserProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", unique=True, ondelete="CASCADE", index=True
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )

    user: User = Relationship(back_populates="profile")


class UserProfilePublic(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# UserRaceInteraction - Tracks views, saves, and shares for recommendations
# =============================================================================


class UserRaceInteraction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", ondelete="CASCADE", index=True
    )
    race_id: uuid.UUID = Field(
        foreign_key="race.id", ondelete="CASCADE", index=True
    )
    action: InteractionTypeEnum
    created_at: datetime = Field(
        default_factory=get_datetime_utc, sa_column=Column(DateTime(timezone=True))
    )


class UserRaceInteractionPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    race_id: uuid.UUID
    action: InteractionTypeEnum
    created_at: datetime


# =============================================================================
# Vietnam Administrative Master Data
# =============================================================================


class AdministrativeRegion(SQLModel, table=True):
    __tablename__ = "administrative_regions"

    id: int = Field(primary_key=True)
    name: str = Field(max_length=255)
    name_en: str = Field(max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    code_name_en: str | None = Field(default=None, max_length=255)


class AdministrativeRegionPublic(SQLModel):
    id: int
    name: str
    name_en: str
    code_name: str | None = None
    code_name_en: str | None = None


class AdministrativeUnit(SQLModel, table=True):
    __tablename__ = "administrative_units"

    id: int = Field(primary_key=True)
    full_name: str | None = Field(default=None, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    short_name: str | None = Field(default=None, max_length=255)
    short_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    code_name_en: str | None = Field(default=None, max_length=255)

    provinces: list["Province"] = Relationship(back_populates="administrative_unit")
    wards: list["Ward"] = Relationship(back_populates="administrative_unit")


class AdministrativeUnitPublic(SQLModel):
    id: int
    full_name: str | None = None
    full_name_en: str | None = None
    short_name: str | None = None
    short_name_en: str | None = None
    code_name: str | None = None
    code_name_en: str | None = None


class Province(SQLModel, table=True):
    __tablename__ = "provinces"

    code: str = Field(primary_key=True, max_length=20)
    name: str = Field(max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str = Field(max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    administrative_unit_id: int | None = Field(
        default=None, foreign_key="administrative_units.id", index=True
    )

    administrative_unit: AdministrativeUnit | None = Relationship(
        back_populates="provinces"
    )
    wards: list["Ward"] = Relationship(back_populates="province")


class ProvincePublic(SQLModel):
    code: str
    name: str
    name_en: str | None = None
    full_name: str
    full_name_en: str | None = None
    code_name: str | None = None
    administrative_unit_id: int | None = None


class ProvincePublicWithDetails(ProvincePublic):
    administrative_unit: AdministrativeUnitPublic | None = None


class ProvincesPublic(SQLModel):
    data: list[ProvincePublic]
    count: int


class Ward(SQLModel, table=True):
    __tablename__ = "wards"

    code: str = Field(primary_key=True, max_length=20)
    name: str = Field(max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    province_code: str | None = Field(
        default=None, foreign_key="provinces.code", index=True
    )
    administrative_unit_id: int | None = Field(
        default=None, foreign_key="administrative_units.id", index=True
    )

    province: Province | None = Relationship(back_populates="wards")
    administrative_unit: AdministrativeUnit | None = Relationship(
        back_populates="wards"
    )


class WardPublic(SQLModel):
    code: str
    name: str
    name_en: str | None = None
    full_name: str | None = None
    full_name_en: str | None = None
    code_name: str | None = None
    province_code: str | None = None
    administrative_unit_id: int | None = None


class WardPublicWithDetails(WardPublic):
    administrative_unit: AdministrativeUnitPublic | None = None


class WardsPublic(SQLModel):
    data: list[WardPublic]
    count: int


# =============================================================================
# End of Vietnam Administrative Master Data
# =============================================================================


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
