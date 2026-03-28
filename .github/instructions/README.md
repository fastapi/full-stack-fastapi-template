# Agent Instructions

This directory contains specialized instruction files that guide AI agents (like GitHub Copilot) when working with specific parts of the codebase.

## Instruction Files

### 1. Backend Python Instructions
**File:** `backend-python.instructions.md`  
**Applies to:** `backend/**/*.py` (excluding tests)

Provides guidance for:
- SQLModel model patterns (Base, Create, Update, Table, Public models)
- CRUD operations with proper session handling
- FastAPI route patterns and dependency injection
- Database queries with SQLModel
- Security best practices
- Import organization

### 2. Frontend React Instructions
**File:** `frontend-react.instructions.md`  
**Applies to:** `frontend/src/**/*.{ts,tsx}` (excluding tests and generated code)

Provides guidance for:
- React component structure and organization
- TanStack Query for data fetching (queries and mutations)
- TanStack Router for routing
- TypeScript patterns and type safety
- shadcn/ui component usage
- Tailwind CSS styling conventions
- Custom hooks usage
- Form handling and validation

### 3. Testing Instructions
**File:** `testing.instructions.md`  
**Applies to:** `backend/tests/**/*.py` and `frontend/tests/**/*.{ts,spec.ts}`

Provides guidance for:
- Pytest patterns for backend testing
- Playwright patterns for frontend E2E testing
- Test fixtures and utilities
- API endpoint testing
- CRUD operation testing
- Permission and authentication testing
- Form and UI interaction testing

### 4. Database Migration Instructions
**File:** `database-migrations.instructions.md`  
**Applies to:** `backend/alembic/**/*.py` and `backend/alembic.ini`

Provides guidance for:
- Creating and applying Alembic migrations
- Common migration patterns (add column, rename, indexes, foreign keys)
- Data migration patterns
- Migration testing and troubleshooting
- Best practices for reversible migrations
- Environment-specific considerations

## Workspace-Level Instructions

**File:** `../.github/copilot-instructions.md`

This file contains general project instructions that apply to the entire workspace, including:
- Project overview and technology stack
- Directory structure
- Development workflows
- Common tasks and patterns
- Security considerations
- Environment setup

## How These Work

These instruction files are automatically detected by GitHub Copilot and used to provide context-aware assistance when you're working on files that match the `applyTo` patterns defined in each file's frontmatter.

For example:
- When editing a file in `backend/app/api/routes/`, the **Backend Python Instructions** will be loaded
- When editing a React component in `frontend/src/components/`, the **Frontend React Instructions** will be loaded
- When editing a test file, the **Testing Instructions** will be loaded

## Updating Instructions

If you need to update these instructions:
1. Edit the relevant `.instructions.md` file
2. Keep the YAML frontmatter intact (between the `---` markers)
3. Ensure the `applyTo` patterns are correct
4. Test with Copilot to verify the instructions are being applied

## Template Source

This project is based on the [FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template).

For more information about the template and its conventions, see:
- Project README: `/README.md`
- Development Guide: `/development.md`
- Backend README: `/backend/README.md`
- Frontend README: `/frontend/README.md`
