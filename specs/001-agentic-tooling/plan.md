# Implementation Plan: Agentic Development Infrastructure

**Branch**: `001-agentic-tooling` | **Date**: 2026-03-08 | **Spec**: `specs/001-agentic-tooling/spec.md`
**Input**: Feature specification from `/specs/001-agentic-tooling/spec.md`

## Summary

Add the developer tooling layer that makes this repository AI-agent-native: structured
rule files for agent onboarding (`base.md`, `ai-feedback-learning-loop.md`,
`coding-standards.md`), automated AI code review and `@claude` interaction via GitHub
Actions, a CI gate that protects rule files from unapproved changes, shared Claude tool
permissions, GitHub project governance files (CODEOWNERS, PR template), and enforcement
of SpecKit retrospectives via `base.md` rules. No application code (backend, frontend,
database) is modified.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript/Node 22 (frontend)
**Primary Dependencies**: GitHub Actions, `anthropics/claude-code-action@v1.0.70`
**Storage**: N/A — file-based artifacts only, no database changes
**Testing**: CI workflow behavior tested via manual scenario execution (spec acceptance scenarios)
**Target Platform**: GitHub-hosted runners (ubuntu-latest), Claude Code CLI (macOS/Linux)
**Project Type**: Repository configuration / developer tooling — no application code changes
**Performance Goals**: AI code review posts within 5 minutes of PR open (SC-002)
**Constraints**: Must not break existing CI workflows; fork PRs must skip gracefully; `.claude/settings.local.json` must remain gitignored
**Scale/Scope**: Single repository, team of contributors

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Applicability | Status |
|-----------|--------------|--------|
| I. Full-Stack Cohesion | N/A — no API or schema changes | ✅ Pass |
| II. Contract-First API Design | N/A — no new endpoints | ✅ Pass |
| III. Security by Default | APPLIES — CI workflows handle secrets; fork PRs skip gracefully; deny rules block destructive ops | ✅ Pass |
| IV. Test-Enforced Quality | PARTIALLY APPLIES — CI gate is testable; rule/config files have no unit tests (acceptable for file artifacts) | ✅ Pass |
| V. Docker-First Infrastructure | N/A — no new services | ✅ Pass |

**Post-design re-check**: All constitution principles remain satisfied. The CI workflow
design (R-002) ensures secrets are never exposed to fork PRs. The `settings.json` deny
list satisfies Principle III for local development.

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-tooling/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── rule-file-format.md
│   ├── lessons-learned-format.md
│   └── pr-description-convention.md
└── tasks.md             # Phase 2 output (/speckit.tasks command — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# All new files — no changes to backend/ or frontend/ application code.

.agents/
└── rules/
    ├── base.md                          # FR-001, FR-012, FR-013: Project rules + retro enforcement
    ├── ai-feedback-learning-loop.md     # FR-002: AI rule-change proposal process
    └── coding-standards.md             # FR-003: Code quality standards

.claude/
├── settings.json                       # FR-010: Pre-approved tool permissions (team-shared)
└── commands/
    └── speckit.retro.md                # FR-011: Already exists ✅ — no changes needed

.github/
├── CODEOWNERS                          # FR-009: Directory ownership
├── pull_request_template.md            # FR-008: PR checklist template
└── workflows/
    ├── claude.yml                      # FR-005, FR-006: AI code review + @claude mentions
    └── rules-gate.yml                  # FR-007: base.md change protection gate

CLAUDE.md                               # FR-004: Root agent entry point, references base.md
```

**Structure Decision**: All artifacts are configuration files at the repository root level.
No new directories under `backend/` or `frontend/`. The `.agents/` directory is the new
convention for agent-readable rule files, following the pattern established in the spec.

## Complexity Tracking

> No constitution violations. Table not required.
