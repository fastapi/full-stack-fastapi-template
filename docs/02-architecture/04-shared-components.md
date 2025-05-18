# Shared Components

This document explains the shared components that provide common functionality across modules in the modular monolith architecture.

## Overview

Shared components are utilities, models, and services that are used by multiple modules. These components are divided into two main categories:

1. **Core Components** (`app/core/`): Fundamental system-level services
2. **Shared Components** (`app/shared/`): Common utilities and models

## Core Components

### Configuration (`app/core/config.py`)

The configuration system provides application settings from environment variables and defaults:

```python
class Settings(BaseSettings):
    """Application settings."""
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_HOST: str = "localhost:8000"
    SERVER_NAME: str = "FastAPI Template"
    PROJECT_NAME: str = "fastapi-template"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    
    # Initial User
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

Usage:

```python
from app.core.config import settings

# Use settings
database_uri = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
```

### Database (`app/core/db.py`)

Provides database session management and base repository functionality:

```python
# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SessionDep dependency
def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    Yields:
        Database session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Use in FastAPI
SessionDep = Annotated[Session, Depends(get_db)]
```

### Security (`app/core/security.py`)

Handles authentication and password hashing:

```python
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash from plain password."""
    return pwd_context.hash(password)

# JWT tokens
def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### Logging (`app/core/logging.py`)

Provides consistent logging across the application:

```python
def get_logger(name: str) -> logging.Logger:
    """
    Get logger for module.
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Add handlers if not already added
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(console_handler)
    
    return logger
```

Usage:

```python
from app.core.logging import get_logger

logger = get_logger("module_name")
logger.info("This is an info message")
logger.error("This is an error message")
```

### Events (`app/core/events.py`)

The event system for inter-module communication:

```python
# Event handler registry
_event_handlers: Dict[str, List[Callable]] = {}

# Event handler decorator
def event_handler(event_type: str) -> Callable:
    """Register an event handler."""
    def decorator(func: Callable) -> Callable:
        if event_type not in _event_handlers:
            _event_handlers[event_type] = []
        _event_handlers[event_type].append(func)
        logger.info(f"Registered handler {func.__name__} for event {event_type}")
        return func
    return decorator

# Publish event
def publish_event(event: EventBase) -> None:
    """Publish an event."""
    event_type = event.event_type
    logger.info(f"Publishing event {event_type}")
    
    if event_type in _event_handlers:
        for handler in _event_handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling event {event_type} with handler {handler.__name__}: {e}")
    else:
        logger.info(f"No handlers registered for event {event_type}")
```

## Shared Components

### Base Models (`app/shared/models.py`)

Provides base models for all domain entities:

```python
class BaseModel(SQLModel):
    """Base model with common properties for all models."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
```

All database models should inherit from this base model to ensure consistent timestamps.

### Exceptions (`app/shared/exceptions.py`)

Custom exceptions for domain-specific error handling:

```python
class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(APIException):
    """Exception for not found errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class ValidationException(APIException):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class AuthenticationException(APIException):
    """Exception for authentication errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)

class AuthorizationException(APIException):
    """Exception for authorization errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=403)
```

Usage:

```python
from app.shared.exceptions import NotFoundException

def get_user(user_id: uuid.UUID) -> User:
    """Get user by ID."""
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found")
    return user
```

### Utils (`app/shared/utils.py`)

Common utility functions used across modules:

```python
def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> bool:
    """
    Send email using templates.
    
    Args:
        email_to: Recipient email
        subject_template: Subject template
        html_template: HTML template
        environment: Template variables
        
    Returns:
        Success status
    """
    # Implementation...

def generate_random_string(length: int = 32) -> str:
    """
    Generate random string.
    
    Args:
        length: String length
        
    Returns:
        Random string
    """
    return secrets.token_urlsafe(length)
```

## API Dependencies (`app/api/deps.py`)

Common dependencies for API routes:

```python
# Current user dependency
def get_current_user(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get current user from token.
    
    Args:
        session: Database session
        token: JWT token
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user is not found
    """
    # Implementation...

# Typed dependencies for better IDE support and documentation
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSuperuser = Annotated[User, Depends(get_current_superuser)]
```

Usage in routes:

```python
@router.get("/users/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return current_user
```

## How to Use Shared Components

### Using Core Components

Example of using core components:

```python
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import get_password_hash

# Initialize logger
logger = get_logger("my_module")

# Use settings
api_url = f"http://{settings.SERVER_HOST}{settings.API_V1_STR}"

# Hash password
hashed_password = get_password_hash("my_secure_password")
```

### Using Shared Models

Example of creating a new model with shared base:

```python
from sqlmodel import Field, SQLModel
from app.shared.models import BaseModel

class Product(BaseModel, table=True):
    """Product model."""
    __tablename__ = "product"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    price: float
    description: Optional[str] = Field(default=None, max_length=1000)
```

### Using Shared Exceptions

Example of using domain exceptions:

```python
from app.shared.exceptions import NotFoundException, ValidationException

def get_product(product_id: uuid.UUID) -> Product:
    """Get product by ID."""
    product = session.get(Product, product_id)
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")
    return product

def create_product(name: str, price: float) -> Product:
    """Create new product."""
    if price <= 0:
        raise ValidationException("Price must be greater than zero")
    
    # Create product
    # ...
```

## Best Practices

1. **Use Shared Components**: Prefer shared components over duplicating functionality
2. **Extend Don't Modify**: Extend shared components for specific needs rather than modifying them
3. **Domain Exceptions**: Use domain-specific exceptions for better error handling
4. **Consistent Logging**: Use the logging utility in all modules
5. **Configuration Access**: Access settings through the central configuration

## Next Steps

- [Extending the API](../04-guides/01-extending-the-api.md)
- [Database Migrations](../03-development-workflow/05-database-migrations.md)