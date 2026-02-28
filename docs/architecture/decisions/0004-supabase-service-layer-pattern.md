---
title: "ADR-0004: Supabase Service Layer Pattern"
doc-type: reference
status: accepted
date: 2026-02-28
decision-makers: ["@team"]
last-updated: 2026-02-28
updated-by: "architecture-docs-writer"
related-code:
  - backend/app/services/**
  - backend/app/models/entity.py
  - backend/app/core/errors.py
related-docs:
  - docs/architecture/overview.md
  - docs/data/models.md
tags: [architecture, adr, service-layer, supabase]
---

# ADR-0004: Supabase Service Layer Pattern

## Context and Problem Statement

The template is transitioning from a SQLAlchemy/SQLModel ORM stack to Supabase as the primary data persistence layer. New domain resources (starting with Entity) need a consistent pattern for encapsulating business logic and Supabase REST client interactions. The existing `crud.py` module uses SQLModel sessions and ORM queries, which are incompatible with the Supabase REST table builder API. A new service layer pattern is needed that works with the Supabase client while maintaining testability, error consistency, and separation of concerns.

<!-- OPTIONAL -->
## Decision Drivers

- **Testability** -- Service functions must be unit-testable without a live database or Supabase instance
- **Consistency with error framework** -- All failures must propagate as `ServiceError` exceptions with structured `ENTITY_*` codes, matching the unified error handling framework (ADR-0001)
- **Stateless simplicity** -- Avoid class-based repository objects or singletons that complicate dependency injection in FastAPI
- **Migration path** -- The pattern must coexist with legacy `crud.py` ORM functions during the incremental migration (AYG-65 through AYG-74)
<!-- /OPTIONAL -->

## Considered Options

1. **Module-level service functions with injected Supabase client** -- Stateless functions that accept `supabase.Client` as the first parameter; DI happens at the route handler level via FastAPI `Depends`
2. **Class-based repository pattern** -- A `EntityRepository` class instantiated with the Supabase client, following the traditional repository pattern with methods like `.create()`, `.get()`, `.list()`
3. **Extend existing `crud.py` with Supabase support** -- Add Supabase-aware functions alongside the existing SQLModel functions in the monolithic `crud.py` module

<!-- OPTIONAL -->
### Option 1: Module-level service functions with injected client

**Pros:**
- Simplest possible API: plain functions with explicit parameters
- Trivially mockable in tests -- pass a `MagicMock()` as the first argument
- No class instantiation overhead or lifecycle management
- Each function is independently importable and testable
- Natural fit for FastAPI's functional dependency injection

**Cons:**
- No shared state between calls (must pass client to every function)
- Module-level functions cannot easily share cross-cutting concerns like caching without additional infrastructure

### Option 2: Class-based repository pattern

**Pros:**
- Familiar OOP pattern; encapsulates client reference as instance state
- Can share cross-cutting concerns (logging, caching) via base class methods
- Supports method chaining and composition patterns

**Cons:**
- Adds indirection: requires instantiation and lifecycle management
- More complex mocking: must mock the class or its constructor
- Heavier boilerplate for simple CRUD operations
- FastAPI's `Depends` system works more naturally with functions than class instances

### Option 3: Extend existing `crud.py`

**Pros:**
- Single location for all data access code
- No new architectural pattern to learn

**Cons:**
- Mixes two incompatible client types (SQLModel Session vs Supabase Client) in one module
- `crud.py` would grow unbounded as new resources are added
- Makes it harder to remove legacy ORM code when migration is complete
- No clear separation between legacy and new patterns
<!-- /OPTIONAL -->

## Decision Outcome

**Chosen option:** "Module-level service functions with injected Supabase client"

**Reason:** This approach provides the simplest, most testable pattern for Supabase-backed resources. Plain functions with an explicit `supabase.Client` first parameter are trivially mockable (pass a `MagicMock()`), require no class instantiation, and align naturally with FastAPI's functional dependency injection via `Depends`. The pattern cleanly separates new Supabase-based resources from legacy ORM code in `crud.py`, making the eventual removal of the ORM layer straightforward.

### Positive Consequences

- **Clear separation of concerns** -- Each service module (e.g., `entity_service.py`) owns business logic for one resource, keeping modules focused and small
- **Trivial unit testing** -- All 20 entity service tests run without a database by passing a `MagicMock()` Supabase client; no fixtures, no containers, no network
- **Consistent error propagation** -- All service functions raise `ServiceError` with structured `ENTITY_*` codes, integrating cleanly with the unified error handling framework (ADR-0001)
- **Owner-scoped security** -- Every query includes `.eq("owner_id", owner_id)` filtering, enforcing row-level ownership at the service layer
- **Coexistence with legacy code** -- New service modules live in `backend/app/services/` while legacy `crud.py` remains untouched, enabling incremental migration

### Negative Consequences

- **No shared client state** -- The Supabase client must be passed to every function call, creating slight parameter repetition at the route handler level; mitigated by FastAPI's `Depends` which injects the client once per request
- **No ORM features** -- Supabase REST calls do not provide relationship loading, identity map, or unit-of-work patterns available in SQLAlchemy; mitigated by the fact that the template's CRUD operations are simple and do not require these features
- **Two data access patterns coexist** -- During the migration period, developers must understand both the legacy `crud.py` (SQLModel) and new `services/` (Supabase) patterns; mitigated by clear directory separation and documentation

## Confirmation

The pattern is validated by the 20 passing unit tests in `backend/tests/unit/test_entity_service.py`, which cover all five CRUD operations (create, get, list, update, delete), error propagation for not-found and infrastructure failures, pagination boundary clamping, and the no-op update short-circuit. All tests run in isolation using mocked Supabase clients with no database dependency.
