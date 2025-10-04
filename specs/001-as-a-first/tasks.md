# Tasks: Mermaid ERD Diagram Documentation

**Input**: Design documents from `/specs/001-as-a-first/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume web application structure - adjust based on plan.md structure

## Phase 3.1: Setup
- [x] T001 Create project structure for ERD generation module
- [x] T002 Initialize Python dependencies for ERD generation (SQLModel, Mermaid, pre-commit) using uv in the ./backend directory.
- [x] T003 [P] Configure linting and formatting tools for ERD module
- [x] T003a [P] Add multi-file model discovery capability to ERD Generator

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test CLI interface in tests/contract/test_cli_interface.py
- [x] T005 [P] Contract test pre-commit hook in tests/contract/test_pre_commit_hook.py
- [x] T006 [P] Contract test validation system in tests/contract/test_validation_contract.py
- [x] T007 [P] Integration test ERD generation workflow in tests/integration/test_erd_workflow.py
- [x] T008 [P] Integration test automatic update workflow in tests/integration/test_auto_update.py
- [x] T009 [P] Integration test error handling workflow in tests/integration/test_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T010 [P] ERD Generator entity in backend/app/erd_generator.py
- [x] T011 [P] Model Metadata entity in backend/app/erd_models.py
- [x] T012 [P] ERD Output entity in backend/app/erd_output.py
- [x] T013 [P] Entity Definition entity in backend/app/erd_entities.py
- [x] T014 [P] Field Definition entity in backend/app/erd_fields.py
- [x] T015 [P] Relationship Definition entity in backend/app/erd_relationships.py
- [x] T016 CLI script generate_erd in backend/scripts/generate_erd.py
- [x] T017 Pre-commit hook integration in .pre-commit-config.yaml
- [x] T018 Validation system implementation in backend/app/erd_validation.py

## Phase 3.4: Integration
- [x] T019 Connect ERD Generator to SQLModel introspection
- [x] T020 Integrate CLI with file system operations
- [x] T021 Connect pre-commit hook to ERD generation workflow
- [x] T022 Integrate validation system with ERD generation

## Phase 3.5: Polish
- [x] T023 [P] Unit tests for ERD Generator in tests/unit/test_erd_generator.py
- [x] T024 [P] Unit tests for Model Metadata in tests/unit/test_erd_models.py
- [x] T025 [P] Unit tests for validation system in tests/unit/test_erd_validation.py
- [x] T026 Performance tests for ERD generation (<30 seconds for schemas with up to 20 tables and 100 fields)
- [x] T027 [P] Update documentation in docs/database/erd.md
- [x] T028 [P] Update constitution with ERD requirements in .specify/memory/constitution.md
- [x] T029 [P] Update plan template with ERD checks in .specify/templates/plan-template.md
- [x] T030 [P] Update tasks template with ERD maintenance in .specify/templates/tasks-template.md
- [x] T031 Remove duplication and optimize code
- [x] T032 Run manual-testing.md validation

## Dependencies
- Tests (T004-T009) before implementation (T010-T018)
- T010 blocks T003a (model discovery must be implemented first)
- T003a blocks T019 (discovery needed before SQLModel introspection)
- T016 blocks T020
- T017 blocks T021
- T018 blocks T022
- Implementation before polish (T023-T032)

## Parallel Example
```
# Launch T004-T009 together:
Task: "Contract test CLI interface in tests/contract/test_cli_interface.py"
Task: "Contract test pre-commit hook in tests/contract/test_pre_commit_hook.py"
Task: "Contract test validation system in tests/contract/test_validation_contract.py"
Task: "Integration test ERD generation workflow in tests/integration/test_erd_workflow.py"
Task: "Integration test automatic update workflow in tests/integration/test_auto_update.py"
Task: "Integration test error handling workflow in tests/integration/test_error_handling.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - CLI interface → implementation task
   - Pre-commit hook → integration task
   - Validation system → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - ERD Generator → core implementation task
   - Model Metadata → core implementation task
   - ERD Output → core implementation task
   
3. **From User Stories**:
   - Each story → integration test [P]
   - ERD generation workflow → integration test
   - Automatic update workflow → integration test
   - Error handling workflow → integration test

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
