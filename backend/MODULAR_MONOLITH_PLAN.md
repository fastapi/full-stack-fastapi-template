# Modular Monolith Refactoring Plan

This document outlines a comprehensive plan for refactoring the FastAPI backend into a modular monolith architecture. This approach maintains the deployment simplicity of a monolith while improving code organization, maintainability, and future extensibility.

## Goals

1. Improve code organization through domain-based modules
2. Separate business logic from API routes and data access
3. Establish clear boundaries between different parts of the application
4. Reduce coupling between components
5. Facilitate easier testing and maintenance
6. Allow for potential future microservice extraction if needed

## Module Boundaries

We will organize the codebase into these primary modules:

1. **Auth Module**: Authentication, authorization, JWT handling
2. **Users Module**: User management functionality
3. **Items Module**: Item management (example domain, could be replaced)
4. **Email Module**: Email templating and sending functionality
5. **Core**: Shared infrastructure components (config, database, etc.)

## New Directory Structure

```
backend/
├── alembic.ini               # Alembic configuration
├── app/
│   ├── main.py               # Application entry point
│   ├── api/                  # API routes registration
│   │   └── deps.py           # Common dependencies
│   ├── alembic/              # Database migrations
│   │   ├── env.py            # Migration environment setup
│   │   ├── script.py.mako    # Migration script template
│   │   └── versions/         # Migration versions
│   ├── core/                 # Core infrastructure
│   │   ├── config.py         # Configuration
│   │   ├── db.py             # Database setup
│   │   ├── events.py         # Event system
│   │   └── logging.py        # Logging setup
│   ├── modules/              # Domain modules
│   │   ├── auth/             # Authentication module
│   │   │   ├── api/          # API routes
│   │   │   │   └── routes.py
│   │   │   ├── domain/       # Domain models
│   │   │   │   └── models.py
│   │   │   ├── services/     # Business logic
│   │   │   │   └── auth.py
│   │   │   ├── repository/   # Data access
│   │   │   │   └── auth_repo.py
│   │   │   └── dependencies.py # Module-specific dependencies
│   │   ├── users/            # Users module (similar structure)
│   │   ├── items/            # Items module (similar structure)
│   │   └── email/            # Email services
│   └── shared/               # Shared code/utilities
│       ├── exceptions.py     # Common exceptions
│       ├── models.py         # Shared base models
│       └── utils.py          # Shared utilities
├── tests/                    # Test directory matching production structure
```

## Implementation Phases

### Phase 1: Setup Foundation (2-3 days)

1. Create new directory structure
2. Setup basic module skeletons
3. Update imports in main.py
4. Ensure application still runs with minimal changes

### Phase 2: Extract Core Components (3-4 days)

1. Refactor config.py into a more modular structure
2. Extract db.py and refine for modular usage
3. Create events system for cross-module communication
4. Implement centralized logging
5. Setup shared exceptions and utilities
6. Update Alembic migration environment for modular setup

### Phase 3: Auth Module (3-4 days)

1. Move auth models from models.py to auth/domain/models.py
2. Extract auth business logic to services
3. Create auth repository for data access
4. Move auth routes to auth module
5. Update tests for auth functionality

### Phase 4: Users Module (3-4 days)

1. Move user models from models.py to users/domain/models.py
2. Extract user business logic to services
3. Create user repository
4. Move user routes to users module
5. Update tests for user functionality

### Phase 5: Items Module (2-3 days)

1. Move item models from models.py to items/domain/models.py
2. Extract item business logic to services
3. Create item repository
4. Move item routes to items module
5. Update tests for item functionality

### Phase 6: Email Module (1-2 days)

1. Extract email functionality to dedicated module
2. Create email service with templates
3. Create interfaces for email operations
4. Update services that send emails

### Phase 7: Dependency Management & Integration (2-3 days)

1. Implement dependency injection system
2. Setup module registration
3. Update cross-module dependencies
4. Integrate with event system

### Phase 8: Testing & Refinement (3-4 days)

1. Update test structure to match new architecture
2. Add boundary tests between modules
3. Refine module interfaces
4. Complete documentation

## Handling Cross-Cutting Concerns

### Security

- Extract security utilities to core/security.py
- Create clear interfaces for auth operations
- Use dependency injection for security components

### Logging

- Implement centralized logging in core/logging.py
- Create module-specific loggers
- Standardize log formats and levels

### Configuration

- Maintain centralized config in core/config.py
- Use dependency injection for configuration
- Allow module-specific configuration sections

### Events

- Create a simple pub/sub system in core/events.py
- Use domain events for cross-module communication
- Define standard event interfaces

### Database Migrations

- Keep migrations in the central app/alembic directory
- Update env.py to import models from all modules
- Create a systematic approach for generating migrations
- Document how to create migrations in the modular structure

## Test Coverage

- Maintain existing tests during transition
- Create module-specific test directories
- Implement interface tests between modules
- Use mock objects for cross-module dependencies
- Ensure test coverage remains high during refactoring

## Key Refactorings

### main.py

```python
from fastapi import FastAPI
from app.core.config import settings
from app.api import setup_routers
from app.core.events import setup_event_handlers

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # Setup routers from all modules
    setup_routers(application)
    
    # Setup event handlers
    setup_event_handlers(application)
    
    return application

app = create_application()
```

### models.py to Domain Models

Split models.py into module-specific domain models:

```python
# app/modules/users/domain/models.py
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from app.shared.models import TimestampedModel
import uuid

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class User(UserBase, TimestampedModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    
    # Relationships defined with explicit foreign keys for clarity
```

### crud.py to Repositories

```python
# app/modules/users/repository/user_repo.py
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from app.modules.users.domain.models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
        
    def get(self, user_id: UUID) -> Optional[User]:
        return self.session.get(User, user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
        
    # Additional repository methods
```

### Service Layer

```python
# app/modules/users/services/user_service.py
from typing import Optional, List
from uuid import UUID
from fastapi import Depends
from app.core.db import get_session
from app.modules.users.domain.models import User, UserCreate, UserUpdate
from app.modules.users.repository.user_repo import UserRepository
from app.core.security import get_password_hash

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        
    def create_user(self, user_in: UserCreate) -> User:
        # Business logic for creating users
        hashed_password = get_password_hash(user_in.password)
        user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_superuser=user_in.is_superuser,
        )
        return self.repo.create(user)
        
    # Additional service methods
```

### API Routes

```python
# app/modules/users/api/routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.modules.users.services.user_service import UserService
from app.modules.users.domain.models import UserCreate, UserUpdate, UserPublic
from app.modules.users.dependencies import get_user_service
from app.modules.auth.dependencies import get_current_active_user

router = APIRouter()

@router.get("/users/", response_model=List[UserPublic])
def read_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_active_user),
):
    """
    Retrieve users.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    users = user_service.get_multi(skip=skip, limit=limit)
    return users

# Additional route handlers
```

## Dependency Management Between Modules

1. **Explicit Interfaces**: Define clear interfaces for each module
2. **Dependency Injection**: Use FastAPI's dependency injection system
3. **Repository Pattern**: Isolate data access through repositories
4. **Event-Driven Communication**: Use events for cross-module notifications
5. **Shared Models**: Keep shared models in a common location

## Timeline and Resources

- Total estimated time: 3-4 weeks
- Required resources: 1-2 developers
- Testing requirements: Maintain >90% test coverage

## Database Migration Specifics

### Alembic Environment Setup

```python
# app/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings

# Import all models for Alembic to detect
# This is a key adjustment for the modular structure
from app.modules.auth.domain.models import *  # noqa
from app.modules.users.domain.models import *  # noqa
from app.modules.items.domain.models import *  # noqa
# Import models from other modules as they are added

# Import the shared SQLModel metadata
from sqlmodel import SQLModel

config = context.config
fileConfig(config.config_file_name)
target_metadata = SQLModel.metadata

# ... rest of env.py configuration ...
```

### Migration Strategy

1. **Centralized Migration Repository**: All migrations remain in app/alembic/versions/
2. **Module-Aware Migration Creation**: When creating migrations for a specific module, use a naming convention that indicates the module
3. **Migration Commands**: Create a utility script to generate migrations for specific modules

```bash
# Example script usage
./scripts/create_migration.sh users "Add phone number to user model"
```

### Migration Dependencies

For modules with dependencies on other modules' tables:
1. Use explicit foreign key references with proper ondelete behavior
2. Ensure migration ordering through Alembic dependencies
3. Document relationships between modules in migration files

## Success Criteria

1. All tests pass after refactoring
2. No regression in functionality
3. Clear module boundaries established
4. Improved maintainability metrics
5. Developer experience improvement

## Future Considerations

1. Potential for extracting modules into microservices
2. Adding new modules for additional functionality
3. Scaling individual modules independently
4. Implementing CQRS pattern within modules

This refactoring plan provides a roadmap for transforming the existing monolithic FastAPI application into a modular monolith with clear boundaries, improved organization, and better maintainability.