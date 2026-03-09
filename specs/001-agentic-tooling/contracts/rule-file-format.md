# Contract: Agent Rule File Format

**Applies to**: `.agents/rules/*.md`
**Version**: 1.0
**Enforced by**: CI rules-gate (for `base.md`), CODEOWNERS review (for all files)

---

## File Header (required)

Every rule file MUST start with a level-1 heading and a one-line purpose statement:

```markdown
# [Rule File Title]

> [One sentence: what this file covers and who reads it]
```

---

## Section Structure

Sections are level-2 headings (`##`). Order within a file is flexible, but the
following sections are REQUIRED in `base.md`:

| Section | Required in | Notes |
|---------|------------|-------|
| `## Project Overview` | `base.md` | Stack, architecture diagram (text), key directories |
| `## Available Commands` | `base.md` | Verbatim-executable commands, grouped by category |
| `## Project Structure` | `base.md` | Directory tree, annotated with purpose |
| `## Testing Conventions` | `base.md` | How to run, where tests live |
| `## SpecKit Workflow` | `base.md` | Retro enforcement (FR-012, FR-013) |
| `## Rule Proposal Process` | `base.md` | References `ai-feedback-learning-loop.md` |
| `## SDD Development Workflow` | `base.md` | Branch → PR → CI → review → merge |

---

## Command Block Format

All commands in `## Available Commands` MUST use fenced code blocks with `bash` syntax:

```markdown
### Backend Tests

```bash
uv run bash scripts/tests-start.sh "test run description"
```

### Frontend Lint

```bash
bun run lint
```
```

Commands MUST be copy-pasteable verbatim. Never include placeholder values like
`<project-name>` unless unavoidable, and document the substitution immediately below.

---

## Retro Enforcement Block (base.md only)

The `## SpecKit Workflow` section MUST include the following verbatim text (FR-012):

```markdown
### Retro Gate (mandatory)

After every SpecKit phase command completes (`/speckit.specify`, `/speckit.plan`,
`/speckit.tasks`, `/speckit.implement`), run `/speckit.retro` before starting
the next phase. Do not proceed until the retro produces a "Ready" status.

**Micro-retro** (after each task in `/speckit.implement`):
1. Simplify the code just written
2. Log anything unexpected to `specs/<feature>/lessons-learned.md`
3. Check whether `tasks.md`, `plan.md`, or `spec.md` needs updating
4. Suggest `/clear` before the next task

**Phase retro** (after each phase command):
1. Summarize what was produced
2. Review `lessons-learned.md`
3. Check all earlier artifacts for drift
4. Propose constitution/rules updates (never self-apply — await human approval)
5. Confirm readiness gate (5 items)
6. Suggest `/clear` with specific files to re-read
```

---

## Forbidden Patterns

- No executable code (shell scripts, Python, etc.)
- No hardcoded secrets or credentials
- No references to personal usernames or local machine paths
- No `<!-- TODO -->` comments — open items go to `tasks.md`

---

## Change Control

Changes to `.agents/rules/base.md` MUST include:

```
Rule-Change-Approval: <link or reference to human approval>
```

in the PR description. CI will reject the PR if this line is absent.
All other files in `.agents/rules/` follow normal review via CODEOWNERS.
