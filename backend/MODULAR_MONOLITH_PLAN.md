# Modular Monolith Refactoring Plan

This document outlines a comprehensive plan for refactoring the FastAPI backend into a modular monolith architecture. This approach maintains the deployment simplicity of a monolith while improving code organization, maintainability, and future extensibility.

## Goals

1. ✅ Improve code organization through domain-based modules
2. ✅ Separate business logic from API routes and data access
3. ✅ Establish clear boundaries between different parts of the application
4. ✅ Reduce coupling between components
5. ✅ Facilitate easier testing and maintenance
6. ✅ Allow for potential future microservice extraction if needed

## Module Boundaries

We will organize the codebase into these primary modules:

1. ✅ **Auth Module**: Authentication, authorization, JWT handling
2. ✅ **Users Module**: User management functionality
3. ✅ **Items Module**: Item management (example domain, could be replaced)
4. ✅ **Email Module**: Email templating and sending functionality
5. ✅ **Core**: Shared infrastructure components (config, database, etc.)

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

### Phase 1: Setup Foundation (2-3 days) ✅

1. ✅ Create new directory structure
2. ✅ Setup basic module skeletons
3. ✅ Update imports in main.py
4. ✅ Ensure application still runs with minimal changes

### Phase 2: Extract Core Components (3-4 days) ✅

1. ✅ Refactor config.py into a more modular structure
2. ✅ Extract db.py and refine for modular usage
3. ✅ Create events system for cross-module communication
4. ✅ Implement centralized logging
5. ✅ Setup shared exceptions and utilities
6. ✅ Add initial Alembic setup for modular structure (commented out until transition is complete)

### Phase 3: Auth Module (3-4 days) ✅

1. ✅ Move auth models from models.py to auth/domain/models.py
2. ✅ Extract auth business logic to services
3. ✅ Create auth repository for data access
4. ✅ Move auth routes to auth module
5. ✅ Update tests for auth functionality

### Phase 4: Users Module (3-4 days) ✅

1. ✅ Move user models from models.py to users/domain/models.py
2. ✅ Extract user business logic to services
3. ✅ Create user repository
4. ✅ Move user routes to users module
5. ✅ Update tests for user functionality

### Phase 5: Items Module (2-3 days) ✅

1. ✅ Move item models from models.py to items/domain/models.py
2. ✅ Extract item business logic to services
3. ✅ Create item repository
4. ✅ Move item routes to items module
5. ✅ Update tests for item functionality

### Phase 6: Email Module (1-2 days) ✅

1. ✅ Extract email functionality to dedicated module
2. ✅ Create email service with templates
3. ✅ Create interfaces for email operations
4. ✅ Update services that send emails

### Phase 7: Dependency Management & Integration (2-3 days) ✅

1. ✅ Implement dependency injection system
2. ✅ Setup module registration
3. ✅ Update cross-module dependencies
4. 🔄 Integrate with event system (In Progress)

### Phase 8: Testing & Refinement (3-4 days) 🔄

1. ✅ Update test structure to match new architecture
2. ✅ Add blackbox tests for API contract verification
3. 🔄 Refine module interfaces (In Progress)
4. 🔄 Complete architecture documentation (In Progress)

## Handling Cross-Cutting Concerns

### Security ✅

- ✅ Extract security utilities to core/security.py
- ✅ Create clear interfaces for auth operations
- ✅ Use dependency injection for security components

### Logging ✅

- ✅ Implement centralized logging in core/logging.py
- ✅ Create module-specific loggers
- ✅ Standardize log formats and levels

### Configuration ✅

- ✅ Maintain centralized config in core/config.py
- ✅ Use dependency injection for configuration
- ✅ Allow module-specific configuration sections

### Events 🔄

- ✅ Create a simple pub/sub system in core/events.py
- 🔄 Use domain events for cross-module communication (In Progress)
- 🔄 Define standard event interfaces (In Progress)

### Database Migrations 🔄

- ✅ Keep migrations in the central app/alembic directory
- ✅ Prepare env.py for future model imports (commented structure)
- 🔄 Create a systematic approach for generating migrations
- 🔄 Document how to create migrations in the modular structure

## Test Coverage

- ✅ Maintain existing tests during transition
- ✅ Create module-specific test directories
- 🔄 Implement interface tests between modules (In Progress)
- ✅ Use mock objects for cross-module dependencies
- ✅ Ensure test coverage remains high during refactoring

## Remaining Tasks

### 1. Migrate Remaining Models (High Priority)

- ✅ Move the Message model to shared/models.py
- ✅ Move the TokenPayload model to auth/domain/models.py
- ✅ Confirm NewPassword model already migrated to auth/domain/models.py
- ✅ Move the Token model to auth/domain/models.py
- ✅ Document model migration strategy in MODULAR_MONOLITH_IMPLEMENTATION.md
- 🔄 Update remaining import references for non-table models:
  - ItemsPublic (already duplicated in items/domain/models.py)
  - UsersPublic (already duplicated in users/domain/models.py)
- 🔄 Develop strategy for table models (User, Item) migration

### 2. Complete Event System (Medium Priority)

- ✅ Set up basic event system infrastructure
- 🔄 Document event system structure and usage
- 🔄 Implement user.created event for sending welcome emails
- 📝 Test event system with additional use cases
- 📝 Create examples of inter-module communication via events

### 3. Finalize Alembic Integration (High Priority)

- ✅ Document current Alembic transition approach in MODULAR_MONOLITH_IMPLEMENTATION.md
- 🔄 Update Alembic environment to import models from all modules
- 🔄 Test migration generation with the new modular structure
- 📝 Create migration template for modular table models

### 4. Documentation and Examples (Medium Priority)

- 📝 Update project README with information about the new architecture
- 📝 Add developer guidelines for working with the modular structure
- 📝 Create examples of extending the architecture with new modules

### 5. Cleanup (Low Priority)

- 📝 Remove legacy code and unnecessary comments
- 📝 Clean up any temporary workarounds

## Success Criteria

1. ✅ All tests pass after refactoring
2. ✅ No regression in functionality
3. ✅ Clear module boundaries established
4. ✅ Improved error handling and exception reporting
5. 🔄 Complete model migration (In Progress)
6. 🔄 Developer experience improvement (In Progress)

## Future Considerations

1. Potential for extracting modules into microservices
2. Adding new modules for additional functionality
3. Scaling individual modules independently
4. Implementing CQRS pattern within modules

This refactoring plan provides a roadmap for transforming the existing monolithic FastAPI application into a modular monolith with clear boundaries, improved organization, and better maintainability.

## Estimated Completion

Total estimated time for remaining tasks: 4-7 days with 1 developer.

## Progress Summary

- ✅ Core architecture implementation: **100% complete**
- ✅ Module structure and boundaries: **100% complete**
- ✅ Service and repository layers: **100% complete**
- ✅ Dependency injection system: **100% complete**
- ✅ Shared infrastructure: **100% complete**
- 🔄 Model migration: **40% complete**
- 🔄 Event system: **70% complete**
- 🔄 Documentation: **60% complete**
- 🔄 Testing: **80% complete**

Overall completion: **~85%**