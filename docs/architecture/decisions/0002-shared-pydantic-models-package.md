---
title: "ADR-0002: Shared Pydantic Models Package"
doc-type: reference
status: proposed
date: 2026-02-27
decision-makers: ["@amostan"]
last-updated: 2026-02-27
updated-by: "architecture-docs-writer"
related-code:
  - backend/app/models/__init__.py
  - backend/app/models/common.py
  - backend/app/models/auth.py
related-docs:
  - docs/architecture/overview.md
tags: [architecture, adr, models, pydantic]
---

# ADR-0002: Shared Pydantic Models Package

## Context and Problem Statement

The original codebase used a single `backend/app/models.py` file containing all SQLModel ORM tables, Pydantic request/response schemas, and JWT token types. As the system evolves to support external authentication (Clerk) and standardized API response envelopes, this flat module becomes a mixing ground for unrelated concerns: ORM table definitions, API contract types, and auth identity models. New shared types like `ErrorResponse`, `PaginatedResponse`, and `Principal` do not belong alongside SQLModel table classes.

## Decision Drivers

- Separation of ORM tables (database-coupled) from pure Pydantic models (transport/contract types)
- The `Principal` auth model represents a Clerk JWT identity, not a database entity
- Response envelopes (`ErrorResponse`, `ValidationErrorResponse`, `PaginatedResponse`) are cross-cutting concerns used by the error handling framework and all routes
- Import ergonomics: consuming modules should use `from app.models import ErrorResponse, Principal`

## Considered Options

1. **Models package with domain-specific submodules** - Convert `models.py` to a `models/` package with `common.py` (response envelopes), `auth.py` (Principal), and re-exports via `__init__.py`
2. **Keep single models.py, add new types there** - Append `ErrorResponse`, `Principal`, etc. to the existing flat file
3. **Separate schemas package** - Create a parallel `backend/app/schemas/` package for pure Pydantic types, keep `models.py` for ORM only

### Option 1: Models package with domain-specific submodules

**Pros:**
- Clean separation: `common.py` for transport types, `auth.py` for identity model
- `__init__.py` re-exports maintain backward-compatible import paths
- New submodules can be added per domain without growing a single file
- ORM tables can remain in their own submodule when migrated

**Cons:**
- Requires updating imports if any code used `from app.models import User` (mitigated by `__init__.py` re-exports)

### Option 2: Keep single models.py

**Pros:**
- No structural change, simple to add types

**Cons:**
- File grows unbounded mixing ORM and Pydantic types
- Circular import risk increases as the module grows
- No logical grouping -- auth identity model sits next to database table definitions

### Option 3: Separate schemas package

**Pros:**
- Clear distinction between ORM models and API schemas

**Cons:**
- Introduces a naming convention split (`models` vs `schemas`) that is non-standard in the existing codebase
- Doubles the number of packages to navigate
- Some types (like `Principal`) are neither a "schema" nor a "model" in the traditional ORM sense

## Decision Outcome

**Chosen option:** "Models package with domain-specific submodules"

**Reason:** Converting `models.py` to a `models/` package preserves the existing import convention (`from app.models import ...`) while cleanly separating pure Pydantic types from ORM tables. The `__init__.py` re-exports ensure backward compatibility. Submodules can be added incrementally as the system grows.

### Positive Consequences

- `backend/app/models/common.py` contains only transport types: `ErrorResponse`, `ValidationErrorResponse`, `ValidationErrorDetail`, `PaginatedResponse[T]`
- `backend/app/models/auth.py` contains only the `Principal` identity model, decoupled from database concerns
- `__init__.py` provides a flat re-export surface for consuming modules
- New domain-specific model files can be added without modifying existing submodules

### Negative Consequences

- Existing ORM tables (User, Item, and their variant schemas) have not yet been migrated into the package; they remain in the legacy `models.py` location until subsequent stories complete the migration (mitigated by the incremental migration plan across AYG-65 through AYG-74)
