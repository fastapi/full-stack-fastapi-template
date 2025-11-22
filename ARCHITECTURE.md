# Architecture Guidelines

## Overview
This document defines the strict architectural standards for the project. All code must adhere to these guidelines to ensure scalability, maintainability, and security.

## Responsibilities

### 1. Code Generation & Organization
- **Directory Structure**:
    - `/backend/src/api/`: Controllers/Routes.
    - `/backend/src/services/`: Business Logic.
    - `/backend/src/models/`: Database Models.
    - `/backend/src/schemas/`: Pydantic Schemas/DTOs.
    - `/frontend/src/components/`: UI Components.
    - `/common/types/`: Shared models/types.
- **Separation of Concerns**: Maintain strict separation between frontend, backend, and shared code.
- **Tech Stack**: React/Next.js (Frontend), Python/FastAPI (Backend).

### 2. Context-Aware Development
- **Dependency Flow**: Frontend -> API -> Services -> Models.
- **New Features**: Must be documented here or in `implementation_plan.md` before coding.

### 3. Documentation & Scalability
- **Updates**: Update this file when architecture changes.
- **Docstrings**: All functions and classes must have docstrings.
- **Type Definitions**: Strict typing required (TypeScript for FE, Python Type Hints for BE).

### 4. Testing & Quality
- **Test Files**: Every module must have a corresponding test file in `/tests/`.
- **Frameworks**: Jest (Frontend), Pytest (Backend).
- **Linting**: ESLint/Prettier (Frontend), Ruff/MyPy (Backend).

### 5. Security & Reliability
- **Authentication**: JWT/OAuth2.
- **Data Protection**: TLS, AES-256 for sensitive data.
- **Validation**: Pydantic for all inputs.
- **Error Handling**: Standardized HTTP exceptions.

### 6. Infrastructure & Deployment
- **Files**: `Dockerfile`, `docker-compose.yml`, CI/CD YAMLs.

### 7. Roadmap Integration
- **Tech Debt**: Annotate debt in this document.
