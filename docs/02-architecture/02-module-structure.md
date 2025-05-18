# Module Structure

This document explains the internal structure and organization of modules within the modular monolith architecture.

## Module Organization

Each module is organized in a domain-centric way, following a consistent structure:

```
app/modules/{module_name}/
├── __init__.py              # Module initialization
├── api/                     # API layer
│   ├── __init__.py
│   ├── dependencies.py      # Module-specific dependencies
│   └── routes.py            # API endpoints
├── dependencies.py          # Module-level dependency exports
├── domain/                  # Domain layer
│   ├── __init__.py
│   ├── events.py            # Domain events
│   └── models.py            # Domain models
├── repository/              # Data access layer
│   ├── __init__.py
│   └── {module}_repo.py     # Repository implementation
└── services/                # Business logic layer
    ├── __init__.py
    └── {module}_service.py  # Service implementation
```

## Layer Responsibilities

### API Layer

The API layer is responsible for:

- Defining HTTP endpoints
- Request validation
- Response formatting
- Error handling
- Authorization checks

**Example (from `users/api/routes.py`):**

```python
@router.get("/{user_id}", response_model=UserPublic)
def read_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """
    Get user by ID.
    """
    try:
        user = user_service.get_by_id(user_id)
        return user_service.to_public(user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### Domain Layer

The domain layer defines:

- Data models (SQLModel table models)
- Schema models (Pydantic models for API)
- Domain events
- Value objects
- Business rules and invariants

**Example (from `users/domain/models.py`):**

```python
class UserBase(SQLModel):
    """Base user model with common properties."""
    email: str = Field(max_length=255, index=True)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

class User(UserBase, BaseModel, table=True):
    """Database model for a user."""
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=255)

class UserCreate(UserBase):
    """Model for creating a user."""
    password: str
```

### Repository Layer

The repository layer is responsible for:

- Data access and persistence
- Database queries
- CRUD operations
- Transaction management
- Caching (if implemented)

**Example (from `users/repository/user_repo.py`):**

```python
class UserRepository:
    """Repository for user data access."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def get_by_id(self, user_id: uuid.UUID) -> User:
        """Get user by ID."""
        user = self.session.get(User, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
```

### Service Layer

The service layer contains:

- Business logic
- Complex operations
- Workflow orchestration
- Event publishing
- Integrations with other modules

**Example (from `users/services/user_service.py`):**

```python
class UserService:
    """Service for user management."""

    def __init__(self, user_repo: UserRepository):
        """Initialize service with repository."""
        self.user_repo = user_repo

    def create_user(self, user_create: UserCreate) -> User:
        """Create new user."""
        # Check if user exists
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise ValueError(f"User with email {user_create.email} already exists")

        # Create user
        user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=get_password_hash(user_create.password),
        )

        created_user = self.user_repo.create(user)
        
        # Publish event
        event = UserCreatedEvent(user_id=created_user.id, email=created_user.email)
        event.publish()
        
        return created_user
```

## Module Initialization

Each module exposes an initialization function that registers routes and sets up event handlers:

**Example (from `users/__init__.py`):**

```python
def init_users_module(app: FastAPI) -> None:
    """
    Initialize users module.
    
    This function registers all routes and initializes the module.
    """
    # Import here to avoid circular imports
    from app.modules.users.api.routes import router as users_router

    # Include the router in the application
    app.include_router(users_router, prefix=settings.API_V1_STR)
    
    # Import event handlers to register them
    from app.modules.users.services import user_event_handlers
    
    logger.info("Users module initialized")
```

## Dependency Injection

Each module provides factory functions for its key components:

**Example (from `users/api/dependencies.py`):**

```python
def get_user_repository(session: SessionDep) -> UserRepository:
    """
    Get user repository.
    
    Args:
        session: Database session
        
    Returns:
        User repository
    """
    return UserRepository(session)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Get user service.
    
    Args:
        user_repo: User repository
        
    Returns:
        User service
    """
    return UserService(user_repo)
```

## Module Communication

Modules communicate through:

1. **Events**: For asynchronous communication
2. **Service Interfaces**: For direct synchronous calls (when necessary)

### Event-Based Communication

```python
# Publishing module (users/services/user_service.py)
event = UserCreatedEvent(user_id=created_user.id, email=created_user.email)
event.publish()

# Subscribing module (email/services/email_event_handlers.py)
@event_handler("user.created")
def handle_user_created_event(event: UserCreatedEvent) -> None:
    """Handle user created event by sending welcome email."""
    email_service = get_email_service()
    email_service.send_new_account_email(
        email_to=event.email,
        username=event.email,
        password="**********"  # Password is masked in welcome email
    )
```

### Direct Service Communication (when necessary)

```python
# Getting a service from another module
from app.modules.users.services.user_service import get_user_service

user_service = get_user_service()
user = user_service.get_by_id(user_id)
```

## Best Practices

1. **Keep Domains Separate**: Each module should focus on a single domain
2. **Use Events for Cross-Module Communication**: Prefer events over direct imports
3. **Follow Consistent Patterns**: Use the same structure and patterns across all modules
4. **Use Dependency Injection**: Inject dependencies rather than instantiating them directly
5. **Document Public APIs**: Add clear docstrings to all public methods
6. **Add Comprehensive Tests**: Test each layer of each module

## Next Steps

- Learn about the [Event System](03-event-system.md)
- Explore [Shared Components](04-shared-components.md)
- See how to [Extend the API](../04-guides/01-extending-the-api.md)