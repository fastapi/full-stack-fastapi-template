# Full Stack FastAPI Template Constitution

This document defines the core principles, guidelines, and conventions that govern development practices for this full-stack FastAPI project.

## Core Principles

### I. Project Structure and Conventions
**Follow existing project structure and conventions.**
- Maintain the established directory layout (`backend/`, `frontend/`, `scripts/`, etc.)
- Respect existing file naming conventions (snake_case for Python, kebab-case for frontend)
- Keep separation of concerns between backend and frontend

### II. Backend Technology Stack
**Backend must use FastAPI, SQLModel, Alembic, and PostgreSQL.**
- FastAPI for API framework and routing
- SQLModel for ORM and database models
- Alembic for database migrations
- PostgreSQL as the primary database
- Pydantic v2 for data validation and settings management
- Follow async/await patterns for I/O operations

### III. Frontend Technology Stack
**Frontend must follow existing React + TypeScript patterns.**
- React 19+ with TypeScript
- TanStack Router for routing
- TanStack Query for data fetching
- Tailwind CSS + shadcn/ui for styling
- Zod for frontend validation
- React Hook Form for form management
- Maintain component structure and patterns

### IV. Code Modification Guidelines
**Do not refactor unrelated code unless explicitly requested.**
- Make minimal, focused changes
- Avoid "while you're at it" refactoring
- Preserve existing functionality and behavior
- Only modify code directly related to the requested feature or fix

### V. Authentication and Authorization
**Authentication, authorization, and existing API contracts must not break.**
- Maintain JWT-based authentication system
- Preserve existing authorization checks and permissions
- Do not modify API endpoints without considering backward compatibility
- Keep existing password hashing and security practices
- Maintain email-based password recovery functionality

### VI. API Development Standards
**All new features must include API schemas, validation, and tests where applicable.**
- Define Pydantic models for all request/response schemas
- Use FastAPI's dependency injection for shared logic
- Write tests using pytest for backend endpoints
- Include validation for all inputs and outputs
- Document APIs using OpenAPI/Swagger annotations
- Generate frontend client types from OpenAPI schema

### VII. Development Approach
**Prefer small, incremental changes over large rewrites.**
- Break down features into small, testable units
- Make changes in logical, reviewable increments
- Ensure each change can be tested independently
- Avoid monolithic commits or pull requests

### VIII. Specification-Driven Development
**Specs are the source of truth; code must align with specs.**
- Follow specifications and requirements precisely
- When specs change, update code accordingly
- Document deviations from specs if necessary
- Ensure implementation matches documented behavior

## Additional Guidelines

### Code Quality
- Use type hints for all Python functions
- Follow PEP 8 style guidelines (enforced by Ruff)
- Use strict type checking with mypy
- Write self-documenting code with clear variable names
- Handle errors explicitly with proper exception types
- Use early returns and guard clauses for error handling

### Testing
- Write unit tests for business logic
- Write integration tests for API endpoints
- Maintain test coverage standards
- Use pytest fixtures for test setup
- Test both success and error cases
- Include Playwright tests for critical frontend flows

### Database
- Always use Alembic migrations for schema changes
- Never modify database schema directly
- Test migrations in both directions (upgrade/downgrade)
- Use SQLModel models consistently
- Follow existing patterns for relationships and indexes

### API Design
- Use RESTful conventions for endpoint naming
- Follow existing API versioning patterns
- Return appropriate HTTP status codes
- Use consistent error response formats
- Implement proper pagination for list endpoints
- Use dependency injection for shared dependencies

### Frontend Development
- Use TypeScript strictly (no `any` types)
- Follow React best practices (hooks, functional components)
- Maintain component composition patterns
- Use TanStack Query for all API calls
- Generate client types from OpenAPI schema
- Follow existing UI/UX patterns and components

### Security
- Never commit secrets or credentials
- Use environment variables for configuration
- Validate and sanitize all user inputs
- Use parameterized queries (SQLModel handles this)
- Follow OWASP security best practices
- Keep dependencies up to date

### Docker and Deployment
- Maintain Docker Compose configuration
- Keep Dockerfiles optimized and secure
- Use multi-stage builds where appropriate
- Document environment variables
- Follow existing deployment patterns

### Git and Version Control
- Write clear, descriptive commit messages
- Create focused pull requests
- Keep commits atomic and logical
- Review changes before committing
- Follow existing branching strategies

## Governance

These guidelines should be followed in all development work. When in doubt:
1. Check existing code patterns
2. Review similar implementations
3. Consult project documentation
4. Ask for clarification rather than making assumptions

This constitution supersedes all other practices. Amendments require:
- Documentation with rationale
- Communication to all contributors
- Reflection in code reviews and development practices

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
