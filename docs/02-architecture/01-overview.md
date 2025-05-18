# Architecture Overview

This project uses a **Modular Monolith** architecture for the backend, which combines the deployment simplicity of a monolithic application with the clear boundaries and maintainability benefits of a modular design.

## Core Architecture Principles

The architecture is built on these key principles:

1. **Domain-Based Modules**: Code is organized into cohesive modules based on business domains, rather than technical layers
2. **Clear Module Boundaries**: Each module has well-defined interfaces and responsibilities
3. **Low Coupling**: Modules communicate through events and well-defined interfaces, not direct imports
4. **High Cohesion**: Related functionality is grouped together within each module
5. **Single Responsibility**: Each component has a clear, focused purpose
6. **Dependency Injection**: Dependencies are injected rather than imported directly

## Architecture Diagram

```
+----------------------------------+
|          FastAPI App             |
+----------------------------------+
              |
              v
+----------------------------------+
|          API Layer               |
|    Routes, Deps, Middleware      |
+----------------------------------+
              |
              v
+----------------------------------+
|                                  |
|  +----------+     +----------+   |
|  |  Auth    |     |  Users   |   |
|  | Module   | <-> | Module   |   |
|  +----------+     +----------+   |
|                                  |
|  +----------+     +----------+   |
|  |  Items   |     |  Email   |   |
|  | Module   | <-> | Module   |   |
|  +----------+     +----------+   |
|                                  |
+----------------------------------+
              |
              v
+----------------------------------+
|        Database Layer            |
|        (PostgreSQL)              |
+----------------------------------+
```

## Implementation Status

The modular monolith architecture has been successfully implemented with the following features:

1. ✅ Domain-Based Module Structure
2. ✅ Repository Pattern for Data Access
3. ✅ Service Layer for Business Logic
4. ✅ Dependency Injection
5. ✅ Shared Components
6. ✅ Cross-Cutting Concerns
7. ✅ Module Initialization Flow
8. ✅ Event-Based Communication Between Modules

## Module Structure

Each domain module follows a consistent layered architecture:

```
app/modules/{module_name}/
├── __init__.py              # Module initialization and configuration
├── api/                     # API routes and dependencies
│   ├── __init__.py
│   ├── dependencies.py      # Module-specific dependencies
│   └── routes.py            # API endpoints
├── dependencies.py          # Module-level dependency exports
├── domain/                  # Domain models and business rules
│   ├── __init__.py
│   ├── events.py            # Domain events
│   └── models.py            # Domain models (Pydantic & SQLModel)
├── repository/              # Data access layer
│   ├── __init__.py
│   └── {module}_repo.py     # Repository implementation
└── services/                # Business logic
    ├── __init__.py
    └── {module}_service.py  # Service implementation
```

## Key Components

### Module Initialization

Each module is initialized through a standardized process:

```python
def init_users_module(app: FastAPI) -> None:
    # Import here to avoid circular imports
    from app.modules.users.api.routes import router as users_router

    # Include the users router in the application
    app.include_router(users_router, prefix=settings.API_V1_STR)
    
    # Initialize event handlers 
    from app.modules.users.services import event_handlers
    
    logger.info("Users module initialized")
```

### Layered Architecture

Within each module, code is organized into layers:

1. **API Layer**: FastAPI routes and dependencies
2. **Service Layer**: Business logic and workflow orchestration
3. **Repository Layer**: Data access and persistence
4. **Domain Layer**: Domain models and business rules

### Cross-Cutting Concerns

Certain functionalities span across all modules:

1. **Event System**: For inter-module communication
2. **Logging**: Centralized logging configuration
3. **Database Access**: Session management and transaction handling
4. **Security**: Authentication and authorization

## Key Advantages

The modular monolith architecture provides several advantages:

1. **Simpler Deployment**: Deploy and scale the entire application as a single unit
2. **Clear Boundaries**: Well-defined module interfaces prevent spaghetti code
3. **Team Organization**: Teams can own specific modules
4. **Future Flexibility**: Modules can be extracted into microservices if needed
5. **Reduced Development Complexity**: Simpler development workflow compared to microservices
6. **Better Testing**: Modules can be tested in isolation

## Common Challenges and Solutions

### 1. SQLModel Table Duplication

**Challenge:** SQLModel doesn't allow duplicate table definitions with the same name in the SQLAlchemy metadata.

**Solution:**
- Define table models in their respective domain modules
- Ensure consistent table naming across the application
- Use a centralized Alembic configuration that imports all models

### 2. Circular Dependencies

**Challenge:** Module interdependencies can lead to circular imports.

**Solution:**
- Use local imports (inside functions) instead of module-level imports
- Adopt a clear initialization order for modules
- Implement a modular dependency injection system
- Use events for cross-module communication

### 3. FastAPI Dependency Injection

**Challenge:** FastAPI's dependency injection system can be tricky with annotated types and default values.

**Solution:**
- Use consistent parameter ordering in route functions
- Put security dependencies first, then path/query parameters, then service injections

## Next Steps

For more details on specific aspects of the architecture:

- [Module Structure](02-module-structure.md)
- [Event System](03-event-system.md)
- [Shared Components](04-shared-components.md)