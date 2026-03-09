# Tasks: Agentic Development Infrastructure

**Input**: Design documents from `/specs/001-agentic-tooling/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story. All artifacts are file-based — no database,
no application code changes. No tests requested in spec; none included.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup

**Purpose**: Repository configuration prerequisites that all user story phases depend on.

- [x] T001 Add `.claude/settings.local.json` to `.gitignore` at repo root (data-model Entity 5 constraint)

---

## Phase 2: User Story 1 — AI Agent Onboards Without Repeated Corrections (Priority: P1) MVP

**Goal**: Structured rule files in `.agents/rules/` give any AI agent full project context on
first session. A documented feedback loop turns corrections into durable rules.

**Independent Test**: Open a new Claude Code session on a fresh clone; verify the agent can
describe the full-stack architecture, run correct test commands, and propose a rule change
following the documented process — without being prompted.

- [x] T002 [P] [US1] Create `.agents/rules/base.md` with all required sections per
  `specs/001-agentic-tooling/contracts/rule-file-format.md`: Project Overview (stack +
  architecture), Available Commands (verbatim-executable, fenced bash blocks), Project
  Structure (annotated directory tree), Testing Conventions, SpecKit Workflow section with
  verbatim Retro Gate block (FR-012/FR-013), Rule Proposal Process (references
  `ai-feedback-learning-loop.md`), SDD Development Workflow (branch → PR → CI → review →
  merge). No executable code, no hardcoded secrets, no personal paths.
- [x] T003 [P] [US1] Create `.agents/rules/ai-feedback-learning-loop.md` with sections:
  When to Propose a Change, Proposal Format (exact template from data-model Entity 2),
  One-at-a-Time Constraint, Human Approval Required, How to Apply After Approval.
- [x] T004 [P] [US1] Create `.agents/rules/coding-standards.md` with sections: Python
  Standards (ruff config, type annotations, naming, import order), TypeScript Standards
  (ESM-only, naming conventions), Testing Principles (behavior not implementation; mock only
  boundaries), Error Handling (fail fast, clear messages, no swallowed exceptions), Comments
  (self-documenting; no commented-out code).
- [x] T005 [US1] Update `CLAUDE.md` to reference `.agents/rules/base.md` as the single
  source of truth for agent conventions; keep content minimal (1–2 sentence intro + explicit
  read-first instruction); remove any content that duplicates `base.md` (FR-004).

**Checkpoint**: A new AI session can read `.agents/rules/` and answer architecture/command
questions without human prompting (SC-001).

---

## Phase 3: User Story 2 — Pull Requests Receive Automated AI Code Review (Priority: P2)

**Goal**: Every code-changing PR gets an automated Claude review posted within 5 minutes.
`@claude` mentions in PR/issue comments invoke Claude directly in the same thread.

**Independent Test**: Open a PR with a deliberate issue (e.g., hardcoded credential) → Claude
posts a review identifying it within 5 minutes. Post `@claude explain this function` in a PR
comment → Claude responds in thread.

- [x] T006 [US2] Create `.github/workflows/claude.yml` with two jobs:
  1. `pr-review` — triggered on `pull_request` (opened, synchronize, reopened); fork guard
     `if: github.event.pull_request.head.repo.full_name == github.repository`; docs-only skip
     (preliminary step: `git diff --name-only origin/${{ github.base_ref }}...HEAD` — exit
     early if all changed files match `docs/**`, `*.md`, `*.txt`, `*.rst`); uses
     `anthropics/claude-code-action@26ec041249acb0a944c0a47b6c0c13f05dbc5b44  # v1.0.70`
     with `ANTHROPIC_API_KEY` secret; posts structured review comment.
  2. `claude-interact` — triggered on `issue_comment`, `pull_request_review_comment`,
     `pull_request_review`, `issues`; fires when comment/body contains `@claude`; same
     pinned action; responds in same thread.
  Permissions block: `contents: write`, `pull-requests: write`, `issues: write`,
  `id-token: write`, `actions: read` (R-001, R-002).

**Checkpoint**: 100% of same-repo code PRs receive AI review; docs-only and fork PRs skip
cleanly (SC-002).

---

## Phase 4: User Story 3 — Project Governance Prevents Rule Drift (Priority: P3)

**Goal**: CI blocks any PR that modifies `base.md` without an approval reference. PR template
guides contributors. CODEOWNERS auto-requests reviewers.

**Independent Test**: Open a PR modifying `.agents/rules/base.md` without `Rule-Change-Approval:`
in the PR body → CI fails with an actionable error. Add the line → CI passes.

- [x] T007 [P] [US3] Create `.github/workflows/rules-gate.yml` triggered on `pull_request`
  with `paths: ['.agents/rules/base.md']`. Job checks `github.event.pull_request.body` via
  `echo "$PR_BODY" | grep -q "Rule-Change-Approval:"`. On failure: exit 1 with the exact
  error message from R-005 (instructs developer to add `Rule-Change-Approval: <link>` to PR
  description). On success: exit 0. Apply fork guard consistent with `claude.yml` (R-002).
- [x] T008 [P] [US3] Create `.github/pull_request_template.md` with Summary and Validation
  sections per `specs/001-agentic-tooling/contracts/pr-description-convention.md`. Checklist:
  tests passed locally, docs updated if user-facing behavior changed, frontend client
  regenerated if API schema changed, rule governance note (add `Rule-Change-Approval: <ref>`
  if modifying `.agents/rules/base.md`).
- [x] T009 [US3] Create `.github/CODEOWNERS` with entries for `backend/`, `frontend/`,
  `.github/workflows/`, `.agents/rules/` — replace `@<maintainer>` placeholder with the
  actual GitHub username(s) for this repository (R-006). Verify no placeholder remains before
  committing — invalid CODEOWNERS entries fail silently on GitHub.

**Checkpoint**: PRs touching `base.md` without approval reference are blocked by CI (SC-003).
New contributors see the PR template checklist immediately (SC-005).

---

## Phase 5: User Story 4 — Claude Tool Permissions Pre-Configured (Priority: P4)

**Goal**: Shared `.claude/settings.json` pre-approves safe development operations for all
team members; destructive operations still require explicit confirmation.

**Independent Test**: Clone project, open Claude Code, run backend tests and frontend linters
without permission prompts. Attempt `git push --force` — confirm prompt appears.

- [x] T010 [US4] Update `.claude/settings.json` with allow/deny arrays per data-model Entity 5:
  **Allow**: `Bash(uv run pytest *)`, `Bash(uv run python -m pytest *)`, `Bash(uv run ruff *)`,
  `Bash(uv run *)`, `Bash(bun run *)`, `Bash(bunx *)`, `Bash(docker compose *)`,
  `Bash(git status)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git fetch *)`,
  `Bash(git add *)`, `Bash(git commit *)`, `Bash(git checkout *)`, `Bash(git branch *)`,
  `Bash(.specify/scripts/bash/*)`, `Bash(cat *)`, `Bash(ls *)`, `Bash(fd *)`, `Bash(rg *)`.
  **Deny**: `Bash(git push --force*)`, `Bash(git push *--force*)`, `Bash(git reset --hard *)`,
  `Bash(rm -rf *)`, `Bash(rm -fr *)`, `Bash(sudo *)` (R-003).

**Checkpoint**: All common dev operations run without prompts; force-push and hard-reset
require confirmation (SC-004).

---

## Phase 6: User Story 5 — SpecKit Phases Followed by Structured Retrospectives (Priority: P5)

**Goal**: `base.md` mandates retro gates after every SpecKit phase. The existing
`speckit.retro` skill covers both retro modes. No new skill file needed.

**Independent Test**: With `base.md` in place, start a SpecKit workflow. After each phase,
verify the agent pauses, runs the retro, and suggests `/clear` with specific re-read
instructions before proceeding.

- [x] T011 [US5] Verify `.claude/commands/speckit.retro.md` exists and contains both
  micro-retro mode (Simplify → Quick Learning Check → Iterate Check → `/clear` suggestion)
  and phase-retro mode (Summarize → Learning Review → Backwards Artifact Check → Propose
  Rules Updates → Readiness Gate → Session Hygiene Suggestion). Confirm T002's `base.md`
  includes the verbatim Retro Gate block from `contracts/rule-file-format.md` covering both
  modes (FR-012, FR-013). No file changes needed if both are already correct (R-004).

**Checkpoint**: Agent never transitions between SpecKit phases without an explicit Ready/Blocked
readiness statement (SC-007). Micro-retro fires after every task (SC-006).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T012 [P] Verify `CLAUDE.md` contains no content that duplicates `base.md` — if any
  duplicate sections remain, remove them from `CLAUDE.md` (FR-004 constraint: `base.md` is
  canonical).
- [x] T013 [P] Verify all `.agents/rules/*.md` files comply with rule-file-format.md
  Forbidden Patterns: no executable code, no hardcoded secrets, no personal usernames or
  local paths, no `<!-- TODO -->` comments.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US1)**: Depends on Phase 1. T002, T003, T004 are parallel; T005 depends on T002
- **Phase 3 (US2)**: Depends on Phase 1 only — independent of US1
- **Phase 4 (US3)**: Depends on Phase 1 only — independent of US1/US2
- **Phase 5 (US4)**: Depends on Phase 1 only — independent of all user stories
- **Phase 6 (US5)**: Depends on T002 (base.md must exist to verify retro sections)
- **Phase 7 (Polish)**: Depends on all prior phases complete

### User Story Dependencies

All user stories depend only on Phase 1 (Setup). They have no dependencies on each other
and can be implemented in parallel by different contributors after T001 is complete.

Exception: T011 (US5) requires T002 to be complete so `base.md` exists to verify.

### Parallel Opportunities

```
After T001:
  T002 || T003 || T004   # All three rule files in parallel
  T006                   # claude.yml independent of rule files
  T007 || T008           # rules-gate and PR template independent of each other
  T010                   # settings.json independent of all above

After T002:
  T005                   # CLAUDE.md update (reads base.md)
  T011                   # retro verification (reads base.md)

After T007, T008:
  T009                   # CODEOWNERS (can go last — needs maintainer username confirmed)

After all phases:
  T012 || T013           # Polish tasks are independent
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: T001
2. Complete Phase 2: T002, T003, T004 in parallel → T005
3. **Stop and validate**: New session → agent describes project without prompting
4. Ship if SC-001 is satisfied

### Full Delivery (All Stories)

1. Phase 1 → Phase 2 (T002–T005)
2. Phase 3 (T006) + Phase 4 (T007–T009) + Phase 5 (T010) in parallel
3. Phase 6 (T011) after T002
4. Phase 7 (T012, T013) last

### Single-Contributor Sequential Order

T001 → T002, T003, T004 (parallel) → T005 → T006 → T007, T008 (parallel) → T009 → T010
→ T011 → T012, T013 (parallel)

---

## Notes

- All tasks produce file artifacts only — no database migrations, no application code changes
- CODEOWNERS (T009): **do not commit with `@<maintainer>` placeholder** — GitHub silently
  ignores invalid entries and CODEOWNERS protection will not work
- `.claude/settings.local.json` must never be committed (T001 ensures this)
- Tests: not requested in spec; none included
- Each phase is independently verifiable against the acceptance scenarios in spec.md
