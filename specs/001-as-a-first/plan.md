# Implementation Plan: Mermaid ERD Diagram Documentation

**Branch**: `001-as-a-first` | **Date**: 2024-12-19 | **Spec**: `/specs/001-as-a-first/spec.md`
**Input**: Feature specification from `/specs/001-as-a-first/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Generate Mermaid ERD diagrams from SQLModel database models with automatic updates via git pre-commit hooks, integrated into project documentation standards and constitution requirements.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: SQLModel, Mermaid, Git hooks, pre-commit framework  
**Storage**: File-based ERD output (Markdown/Mermaid format)  
**Testing**: pytest for unit tests, pre-commit hooks for integration  
**Target Platform**: Cross-platform (Linux/macOS/Windows)  
**Project Type**: web (FastAPI + React full-stack template)  
**Performance Goals**: Reasonable generation time for typical database schemas  
**Constraints**: Must work in Docker environment, fail-fast error handling  
**Scale/Scope**: Single project template with extensible model support

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Full-Stack Integration**: ✅ YES - Requires backend model parsing, documentation updates, and git workflow integration
**Test-Driven Development**: ✅ YES - Test scenarios defined for ERD generation, validation, and error handling
**Auto-Generated Client**: ❌ NO - This is documentation generation, not API client generation
**Docker-First**: ✅ YES - ERD generation must work in containerized environment
**Security by Default**: ✅ YES - Input validation for model parsing, secure file handling

## Project Structure

### Documentation (this feature)
```
specs/001-as-a-first/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── app/
│   ├── models.py        # Existing SQLModel definitions
│   └── erd_generator.py # New ERD generation module
├── scripts/
│   └── generate_erd.py  # CLI script for ERD generation
└── tests/
    ├── unit/
    │   └── test_erd_generator.py
    └── integration/
        └── test_erd_workflow.py

.git/
└── hooks/
    └── pre-commit       # Updated to include ERD generation

docs/
└── database/
    └── erd.md          # Generated ERD documentation

.specify/
├── memory/
│   └── constitution.md  # Updated with ERD requirements
└── templates/
    ├── plan-template.md # Updated with ERD checks
    └── tasks-template.md # Updated with ERD maintenance
```

**Structure Decision**: Web application structure with backend focus, documentation integration, and git workflow enhancement

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Mermaid ERD syntax and best practices for SQLModel relationships
   - Git pre-commit hook integration patterns
   - SQLModel introspection and parsing techniques
   - Documentation integration approaches

2. **Generate and dispatch research agents**:
   ```
   Task: "Research Mermaid ERD syntax for SQLModel relationships and foreign keys"
   Task: "Find best practices for git pre-commit hooks with Python projects"
   Task: "Research SQLModel introspection patterns for automatic schema extraction"
   Task: "Find documentation integration patterns for auto-generated diagrams"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - ERD Generator entity with parsing capabilities
   - Model Metadata entity for SQLModel introspection
   - ERD Output entity for Mermaid diagram structure

2. **Generate API contracts** from functional requirements:
   - CLI interface for manual ERD generation
   - Pre-commit hook integration contract
   - Validation contract for ERD accuracy

3. **Generate contract tests** from contracts:
   - CLI command tests
   - Pre-commit hook integration tests
   - ERD validation tests

4. **Extract test scenarios** from user stories:
   - ERD generation workflow test
   - Automatic update workflow test
   - Error handling workflow test

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - Add ERD generation context to agent guidance

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- ERD Generator module → implementation task [P]
- CLI interface → implementation task [P]
- Pre-commit hook → integration task
- Documentation updates → documentation task [P]
- Constitution updates → governance task [P]

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Core generator → CLI → Integration → Documentation
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Auto-Generated Client: NO | This feature generates documentation, not API clients | N/A - not applicable to documentation generation |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `/memory/constitution.md`*