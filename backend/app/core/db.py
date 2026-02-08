from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Boolean, ForeignKey, func
from datetime import datetime, timezone
from app.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Database Models
class BrandPromptTable(Base):
    """
    The prompts table in the database
    """
    __tablename__ = settings.db_brand_prompts_table_name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand_id = Column(String(100), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=func.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(timezone.utc), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=False)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_brand_id', 'brand_id', 'brand_id'),
        Index('idx_brand_name', 'brand_name', 'brand_name'),
        Index('idx_user_id', 'user_id', 'user_id'),
        Index('idx_idempotency_key', 'idempotency_key', 'idempotency_key'),
        Index('idx_company_id', 'company_id', 'company_id')
    )


class UsersTable(Base):
    """
    The users profile table in the database
    """
    __tablename__ = settings.db_users_table_name

    user_id = Column(String(100), primary_key=True, nullable=False, index=True, unique=True)
    user_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False, index=True, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    password_hash = Column(String(255), nullable=False)

    # relationship with cascading delete
    profile = relationship("UsersProfileTable", backref="user", cascade="all, delete-orphan", passive_deletes=True)
    security = relationship("UsersSecurityTable", backref="user", cascade="all, delete-orphan", passive_deletes=True)
    sessions = relationship("UsersSessionTable", backref="user", cascade="all, delete-orphan", passive_deletes=True)

    # Composite indexes for common queries
    __table_args__ = (Index('idx_email', 'email', 'email'),)


class UsersProfileTable(Base):
    """
    The users profile table in the database
    """
    __tablename__ = settings.db_users_profile_table_name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(100),
        ForeignKey(f"{settings.db_users_table_name}.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)

    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=func.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now(timezone.utc))

    company_id = Column(String(100), nullable=True, index=True)
    job_title = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_id', 'user_id', 'user_id'),
        Index('idx_email', 'email', 'email'),
        Index('idx_company_id', 'company_id', 'company_id')
    )


class UsersSecurityTable(Base):
    # Store user security related information in the database
    __tablename__ = settings.db_users_security_table_name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(100),
        ForeignKey(f"{settings.db_users_table_name}.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    last_login = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)


class UsersSessionTable(Base):
    """
    Store user security related information in the database
    """
    __tablename__ = settings.db_users_session_table_name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(100),
        ForeignKey(f"{settings.db_users_table_name}.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    refresh_token = Column(String(500), nullable=True)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expired_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_id', 'user_id', 'user_id'),
        Index('idx_refresh_token', 'refresh_token', 'refresh_token')
    )


class CompaniesTable(Base):
    """
       The companies table in the database
       """
    __tablename__ = settings.db_companies_table_name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String(100), nullable=False, index=True)
    company_name = Column(String(100), nullable=False, index=True)
    description = Column(String(300), nullable=True)
    email = Column(String(100), nullable=False)
    website = Column(String(100), nullable=True)
    phone = Column(String(100), nullable=True)
    address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_company_name', 'company_name', 'company_name'),
        Index('idx_company_id', 'company_id', 'company_id'),
        Index('idx_email', 'email', 'email')
    )


"""
# disable project table temporary, since we are not using project structure at this time
class ProjectsRecord(Base):
    # the project table in the database
    __tablename__ = settings.db_projects_table_name

    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True, index=False)
    company_id = Column(String(100), nullable=True, index=True)
    created_by = Column(String(100), nullable=False, index=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False, index=False)
    is_active = Column(Boolean, default=True, nullable=False, index=False)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_project_name', 'project_name', 'project_name'),
        Index('idx_company_id', 'company_id', 'company_id'),
    )
"""


"""
# disable prompts running status, since we are not tracking the prompts running status 
class PromptRunningStatus(Base):
    execution_status = Column(
        Enum("success", "failed", "pending", name="execution_status_enum"),
        nullable=False,
        default="pending"
    )
"""


class BrandSearchResultTable(Base):
    __tablename__ = settings.DB_BRAND_SEARCH_RESULT_TABLE_NAME

    # columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    search_instance_id = Column(String(100), nullable=False, index=True)
    user_prompt_id = Column(String(100), nullable=False)
    user_prompt = Column(Text, nullable=False)
    search_target_brand_id = Column(String(100), nullable=False, index=True)
    search_target_brand_name = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False, unique=True, index=True)
    search_return_brand_name = Column(String(100), nullable=False)
    search_return_reason = Column(String(300), nullable=True)
    search_return_ranking = Column(Integer, nullable=False)
    search_return_reference_sources = Column(String(300), nullable=True)
    search_return_customer_review = Column(String(500), nullable=True)
    search_date = Column(DateTime, default=datetime.now().date(), nullable=False)
    model = Column(String(100), nullable=False)

    # index
    __table_args__ = (
        Index('idx_user_prompt_id', 'user_prompt_id', 'user_prompt_id'),
        Index('idx_company_id', 'company_id', 'company_id'),
        Index('idx_search_target_brand_id', 'search_target_brand_id', 'search_target_brand_id'),
        Index('idx_search_instance_id', "search_instance_id", "search_instance_id"),
        Index("idx_search_date", "search_date", "search_date")
    )


class BrandSearchVisibilityTable(Base):
    __tablename__ = settings.DB_BRAND_SEARCH_VISIBILITY_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(String(100), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False, index=True)
    datetime_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    search_date = Column(DateTime, nullable=False, index=True)
    total_search_count = Column(Integer, nullable=False)
    search_visibility_count = Column(Integer, nullable=False)

    __table_args__ = (
        Index('idx_brand_id', 'brand_id', 'brand_id'),
        Index('idx_brand_name', 'brand_name', 'brand_name'),
        Index('idx_search_date', 'search_date', 'search_date'),
    )


class BrandSearchRankingTable(Base):
    __tablename__ = settings.DB_BRAND_SEARCH_RANKING_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(String(100), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False, index=True)
    search_instance_id = Column(String(100), nullable=False)
    datetime_created = Column(DateTime, nullable=False,
                              default=datetime.now(timezone.utc))
    search_date = Column(DateTime, nullable=False, index=True)
    search_return_brand_name = Column(String(100), nullable=True)
    search_ranking = Column(Integer, nullable=False)

    __table_args__ = (
        Index('idx_brand_id', 'brand_id', 'brand_id'),
        Index('idx_brand_name', 'brand_name', 'brand_name'),
        Index('idx_search_date', 'search_date', 'search_date')
    )


class BrandPromptRecordTable(Base):
    """
    The prompts table in the database
    """
    __tablename__ = settings.DB_BRAND_PROMPTS_TABLE_NAME

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    prompt_id = Column(String(100), nullable=False, index=True)
    brand_id = Column(String(100), nullable=False)
    brand_name = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False, unique=True, index=True)
    created_datetime = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_datetime = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=False)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_id', 'user_id', 'user_id'),
        Index('idx_idempotency_key', 'idempotency_key', 'idempotency_key'),
        Index('idx_company_id', 'company_id', 'company_id'),
        Index('idx_brand_id', 'brand_id', 'brand_id'),
        Index('idx_brand_name', 'brand_name', 'brand_name')
    )


# Dependency for database sessions
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified successfully")
