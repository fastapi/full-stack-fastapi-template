# Data Model: Agentic Development Infrastructure

**Phase**: 1 — Design
**Branch**: `001-agentic-tooling`
**Generated**: 2026-03-08

---

> This feature introduces no database changes. All "entities" are files with defined
> schemas. This document specifies the format, required fields, and validation rules
> for each file artifact produced by this feature.

---

## Entity 1: Agent Base Rules File

**File**: `.agents/rules/base.md`
**Role**: Single source of truth for AI agent conventions. Read by all AI agents on
session start. Referenced by `CLAUDE.md`.

### Required Sections

| Section | Purpose | Constraint |
|---------|---------|------------|
| Project Overview | Architecture and stack summary | Must include frontend + backend stacks |
| Available Commands | Exact commands for tests, lint, docker, dev server | Must be executable verbatim |
| Project Structure | Directory tree of key source paths | Must reflect actual repo layout |
| Testing Conventions | How to run, where tests live, coverage expectations | Must reference actual test runners |
| SpecKit Retro Enforcement | Mandates running `/speckit.retro` after every phase | FR-012: This is the enforcement mechanism |
| Both Retro Modes | Defines micro-retro and phase-retro behavior | FR-013: Both modes documented inline |
| SDD Workflow | Feature branch → PR → CI → review → merge | Must reference CODEOWNERS and PR template |
| Rule Proposal Process | How to propose changes (never self-apply) | Must reference `ai-feedback-learning-loop.md` |

### Validation Rules

- MUST NOT contain executable shell scripts (documentation only)
- MUST be kept up to date when stacks or commands change
- Changes MUST include `Rule-Change-Approval:` in the PR description (enforced by CI gate)

---

## Entity 2: AI Feedback Learning Loop

**File**: `.agents/rules/ai-feedback-learning-loop.md`
**Role**: Documents the process for AI agents to propose rule changes and await human
approval before applying them. Prevents silent rule drift.

### Required Sections

| Section | Purpose |
|---------|---------|
| When to Propose a Change | Trigger conditions (correction received, pattern worth preserving) |
| Proposal Format | Structured template for rule change proposals |
| One-at-a-Time Constraint | Only one pending rule change per session |
| Human Approval Required | Clear statement: AI never self-applies rule changes |
| How to Apply After Approval | Steps to update `base.md` once approved |

### Proposal Format (embedded in the file)

```markdown
## Rule Change Proposal

**Triggered by**: [What correction or learning surfaced this]
**Proposed rule**: [Exact text to add/change/remove in base.md]
**Section**: [Which section of base.md this belongs in]
**Rationale**: [Why this is worth preserving project-wide]

Awaiting human approval before applying.
```

---

## Entity 3: Coding Standards

**File**: `.agents/rules/coding-standards.md`
**Role**: Captures agreed-upon code quality standards for AI agents to apply
consistently. Maps to constitution Principle IV (Test-Enforced Quality).

### Required Sections

| Section | Purpose |
|---------|---------|
| Python Standards | ruff config, type annotations, naming, import order |
| TypeScript Standards | biome config, ESM-only, naming conventions |
| Testing Principles | Test behavior not implementation; mock only boundaries |
| Error Handling | Fail fast, clear messages, no swallowed exceptions |
| Comments | Code should be self-documenting; no commented-out code |

---

## Entity 4: CLAUDE.md (Root)

**File**: `CLAUDE.md` (repo root)
**Role**: Entry point for Claude Code. References `.agents/rules/base.md` as the
authoritative source of truth. Kept minimal — delegates to rule files.

### Required Content

- Brief project introduction (1–2 sentences)
- Explicit reference to `.agents/rules/base.md` with instruction to read it first
- Optional: references to `AGENTS.md` / `GEMINI.md` (symlinks to same file)

### Constraint

MUST NOT duplicate content from `base.md`. If information exists in both,
`base.md` is canonical and `CLAUDE.md` should remove the duplicate.

---

## Entity 5: Claude Tool Permissions

**File**: `.claude/settings.json`
**Role**: Shared team permission baseline for Claude Code. Committed to repo.
Controls which Bash commands execute without a confirmation prompt.

### Schema

```json
{
  "permissions": {
    "allow": ["<BashPattern>", ...],
    "deny":  ["<BashPattern>", ...]
  }
}
```

### Bash Pattern Syntax

- `Bash(cmd *)` — matches `cmd` + any arguments (word-boundary prefix match)
- `Bash(cmd)` — exact match with no arguments

### Pre-Approved Commands (allow)

| Category | Patterns |
|----------|---------|
| Backend tests | `Bash(uv run pytest *)`, `Bash(uv run python -m pytest *)` |
| Backend lint | `Bash(uv run ruff *)` |
| Backend tasks | `Bash(uv run *)` |
| Frontend | `Bash(bun run *)`, `Bash(bunx *)` |
| Docker | `Bash(docker compose *)` |
| Git read-only | `Bash(git status)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git fetch *)` |
| Git write | `Bash(git add *)`, `Bash(git commit *)`, `Bash(git checkout *)`, `Bash(git branch *)` |
| SpecKit scripts | `Bash(.specify/scripts/bash/*)` |
| Utilities | `Bash(cat *)`, `Bash(ls *)`, `Bash(fd *)`, `Bash(rg *)` |

### Denied Commands (deny — always require explicit approval)

| Category | Patterns |
|----------|---------|
| Force push | `Bash(git push --force*)`, `Bash(git push *--force*)` |
| Hard reset | `Bash(git reset --hard *)` |
| Destructive delete | `Bash(rm -rf *)`, `Bash(rm -fr *)` |
| Privileged | `Bash(sudo *)` |

### Constraint

`.claude/settings.local.json` MUST be gitignored. Only `settings.json` is committed.

---

## Entity 6: CI Workflow — Claude Actions

**File**: `.github/workflows/claude.yml`
**Role**: Combined workflow for automated PR code review (FR-005) and `@claude` mention
responses (FR-006).

### Triggers

| Job | Trigger | Condition |
|-----|---------|-----------|
| `pr-review` | `pull_request` (opened, synchronize, reopened) | `github.event.pull_request.head.repo.full_name == github.repository` AND changed files include code (not docs-only) |
| `claude-interact` | `issue_comment`, `pull_request_review_comment`, `pull_request_review`, `issues` | Comment/body contains `@claude` |

### Docs-only Skip Logic

For `pr-review`: filter changed file paths. If all changed files match
`docs/**`, `*.md`, `*.txt`, `*.rst` — skip the review job.

GitHub Actions does not support dynamic path filtering in `if` expressions, so
this is implemented via a preliminary step that uses `git diff --name-only` and
exits 0 (with a notice output) if only docs files changed.

### State Transitions

```
PR opened → pr-review triggered
  ├── fork PR? → job skipped (clean)
  ├── docs-only? → job skipped (clean)
  └── code PR from same repo → Claude posts structured review comment

@claude mentioned → claude-interact triggered
  ├── missing ANTHROPIC_API_KEY → action logs error, job fails
  └── key present → Claude responds in same thread
```

---

## Entity 7: CI Workflow — Rules Gate

**File**: `.github/workflows/test-backend.yml` (modified) OR new `rules-gate.yml`
**Role**: Blocks PRs that modify `.agents/rules/base.md` without an approval reference.

### Trigger

```yaml
on:
  pull_request:
    paths:
      - '.agents/rules/base.md'
```

### Validation Logic

Check PR body for `Rule-Change-Approval:` (case-sensitive prefix, any content after
colon). If absent: exit 1 with actionable message. If present: exit 0.

### State Transitions

```
PR modifies base.md
  ├── PR body contains "Rule-Change-Approval:" → gate passes ✅
  └── PR body missing "Rule-Change-Approval:" → gate fails ❌ with error message
```

---

## Entity 8: PR Template

**File**: `.github/pull_request_template.md`
**Role**: Pre-populates PR description with summary section and validation checklist.

### Required Sections

| Section | Purpose |
|---------|---------|
| Summary | What the code does now (imperative, factual) |
| Validation Checklist | Tests run, docs updated if needed, rule governance if applicable |

### Checklist Items

- `[ ]` Tests passed locally
- `[ ]` Docs updated (if user-facing behavior changed)
- `[ ]` Frontend client regenerated (if API changed)
- `[ ]` Rule governance: Add `Rule-Change-Approval: <ref>` if modifying `.agents/rules/base.md`

---

## Entity 9: CODEOWNERS

**File**: `.github/CODEOWNERS`
**Role**: Auto-requests designated reviewers when specific directories are touched.

### Required Entries

```
# Backend source
backend/          @<maintainer>

# Frontend source
frontend/         @<maintainer>

# CI workflows — changes require maintainer review
.github/workflows/ @<maintainer>

# Agent rules — changes require maintainer review (CI gate also applies)
.agents/rules/    @<maintainer>
```

### Constraint

Placeholder `@<maintainer>` MUST be replaced with the actual GitHub username(s)
during implementation. CODEOWNERS is validated by GitHub on push — invalid usernames
cause silent failures.

---

## Entity 10: Lessons-Learned Log

**File**: `specs/<feature>/lessons-learned.md`
**Role**: Accumulates learnings discovered during implementation. Created on demand
by the micro-retro when something unexpected surfaces.

### Format

See `contracts/lessons-learned-format.md` for the full schema.

### Constraint

This file is created per-feature under `specs/<feature>/`. It is NOT a global file.
Each feature has its own log. The retro skill (`speckit.retro.md`) writes to this file
and reads it during phase retros.

---

## Summary: File Inventory

| File | New/Modified | FR |
|------|--------------|----|
| `.agents/rules/base.md` | New | FR-001, FR-012, FR-013 |
| `.agents/rules/ai-feedback-learning-loop.md` | New | FR-002 |
| `.agents/rules/coding-standards.md` | New | FR-003 |
| `CLAUDE.md` | New | FR-004 |
| `.github/workflows/claude.yml` | New | FR-005, FR-006 |
| `.github/workflows/rules-gate.yml` | New | FR-007 |
| `.github/pull_request_template.md` | New | FR-008 |
| `.github/CODEOWNERS` | New | FR-009 |
| `.claude/settings.json` | Modified | FR-010 |
| `.claude/commands/speckit.retro.md` | Already exists ✅ | FR-011 |
| `.agents/rules/base.md` (retro rule) | New (same file) | FR-012, FR-013 |
| `specs/001-agentic-tooling/contracts/` | New | FR-014, FR-015 |
