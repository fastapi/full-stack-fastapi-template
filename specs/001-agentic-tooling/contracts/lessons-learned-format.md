# Contract: Lessons-Learned Log Format

**Applies to**: `specs/<feature>/lessons-learned.md`
**Version**: 1.0
**Written by**: `speckit.retro` skill (micro-retro Step 2, phase retro Step 2)
**Read by**: `speckit.retro` skill (phase retro Step 2), human reviewers

---

## File Header

```markdown
# Lessons Learned: <Feature Name>

**Feature**: `<feature-branch-name>`
**Started**: <ISO date>
```

---

## Entry Format

Each entry is a level-2 heading with the task ID (or phase name) and a short
description. Entries are appended in chronological order — do not reorder.

```markdown
## [Task ID or Phase] — [Short description]

**What happened**: [One sentence: the unexpected event or discovery]
**Impact**: [None | Spec | Plan | Tasks | Architecture] — [brief explanation]
**Proposed action**: [What should change, or "No action — logged for awareness"]
**Status**: [Open | Resolved | Deferred]
```

### Field Rules

| Field | Required | Constraints |
|-------|----------|-------------|
| `What happened` | Yes | One sentence, past tense, factual |
| `Impact` | Yes | One of the listed categories + brief explanation |
| `Proposed action` | Yes | Concrete or explicit "no action" |
| `Status` | Yes | One of: `Open`, `Resolved`, `Deferred` |

---

## Example Entry

```markdown
## T004 — Alembic migration rollback fails on PostgreSQL 15

**What happened**: The `downgrade` function raised a constraint violation because the
column being dropped was referenced by a foreign key not captured in the migration.
**Impact**: Plan — the migration testing step needs an explicit FK drop before column removal.
**Proposed action**: Update `plan.md` migration conventions section to require FK audits.
**Status**: Open
```

---

## Status Transitions

```
Open → Resolved   (human confirmed the artifact was updated)
Open → Deferred   (logged for future but not blocking current phase)
Deferred → Open   (re-prioritized in a later phase)
Deferred → Resolved
```

---

## Constraints

- Entries are append-only. Do not edit or delete prior entries.
- If a prior entry's status changes, add a one-line update under it:
  ```markdown
  **Update (2026-03-10)**: Resolved — plan.md section updated in T008.
  ```
- The file is created when the first unexpected learning surfaces. If no learning
  occurs during a task or phase, the file may not exist (that is acceptable).
- The retro skill checks for the file's existence before reading; no error if absent.
