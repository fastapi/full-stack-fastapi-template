# Research: Agentic Development Infrastructure

**Phase**: 0 — Research
**Branch**: `001-agentic-tooling`
**Generated**: 2026-03-08

---

## R-001: Claude Code GitHub Action

**Decision**: Use `anthropics/claude-code-action` v1.0.70, pinned to SHA.

**Rationale**: The action reached GA with v1.0. It supports two usage modes — interactive
(responds to `@claude` mentions) and automated (runs a prompt directly). A single `claude.yml`
workflow covers both FR-005 (auto code review) and FR-006 (@claude mentions).

**Alternatives considered**:
- Rolling a custom Claude API call via curl — rejected: more maintenance, misses the
  GitHub context injection that the action provides out of the box.
- Using the `@beta` tag — rejected: API changed substantially at v1.0; mutable tags
  are banned by global CLAUDE.md.

**Concrete findings**:

- **Action ref**: `anthropics/claude-code-action@26ec041249acb0a944c0a47b6c0c13f05dbc5b44  # v1.0.70`
- **Required secret**: `ANTHROPIC_API_KEY` (repo Settings → Secrets → Actions)
- **Required workflow permissions**:
  ```yaml
  permissions:
    contents: write
    pull-requests: write
    issues: write
    id-token: write
    actions: read
  ```
- **@claude trigger events**: `issue_comment`, `pull_request_review_comment`,
  `pull_request_review`, `issues`
- **Auto PR review trigger**: `pull_request` with types `[opened, synchronize, reopened]`

---

## R-002: Fork PR Secret Handling

**Decision**: Gate both workflows with
`if: github.event.pull_request.head.repo.full_name == github.repository`
(for `pull_request`) or equivalent comment-author checks (for `issue_comment`).

**Rationale**: The `pull_request` event does not expose secrets to fork PRs. Without
the guard, the job fails loudly instead of skipping gracefully (violates the edge case
in the spec). The guard causes a clean skip (job skipped, no failure), meeting SC-002.

**Alternatives considered**:
- `pull_request_target` — rejected: runs untrusted fork code in the base repo context,
  which is a known security risk and has open bugs with sticky comments (Issue #705) and
  review comment posting (Issue #621).
- Checking `secrets.ANTHROPIC_API_KEY != ''` — rejected: expressions cannot access
  secret values in conditionals; repo identity check is the recommended pattern.

**For @claude workflow**: Filter `issue_comment` events to only internal contributors via
the `if` condition checking `github.event.issue.pull_request` and the action's built-in
`ANTHROPIC_API_KEY` handling (action returns an error if key is missing; job-level condition
prevents execution on fork comment contexts).

---

## R-003: `.claude/settings.json` Permission Format

**Decision**: Use `.claude/settings.json` (committed, team-shared) with pattern-based
`allow` / `deny` arrays. Keep `.claude/settings.local.json` for personal overrides
(gitignored).

**Rationale**: `.claude/settings.json` is the correct shared team file. Arrays merge
across scopes (user global → project → local); deny rules always win.

**Concrete syntax**:
- `Bash(cmd *)` — matches `cmd` + any arguments (word-boundary prefix)
- `Bash(cmd)` — matches `cmd` with no arguments
- Deny rules override allow rules at all scopes

**Pre-approved operations** (from spec FR-010):
- `uv run pytest *`, `uv run ruff *`, `uv run *` (backend)
- `bun run *` (frontend)
- `docker compose *` (infrastructure)
- `git status`, `git diff *`, `git log *`, `git fetch *` (read-only git)
- `git add *`, `git commit *`, `git checkout *`, `git branch *`, `git merge *`

**Denied operations** (always require explicit approval):
- `git push --force*`, `git push *--force*`
- `git reset --hard *`
- `rm -rf *`, `sudo *`

---

## R-004: SpecKit Retro Skill

**Decision**: `speckit.retro.md` already exists in `.claude/commands/` with both
micro-retro and phase-retro modes fully implemented. No new file needed.

**Rationale**: The existing skill covers all acceptance scenarios in User Story 5 and
all FR-011 requirements. The only remaining work is adding the enforcement rule to
`.agents/rules/base.md` (FR-012, FR-013) and ensuring the `lessons-learned.md` format
is documented (FR-015).

**Skill location**: `.claude/commands/speckit.retro.md`

**Modes implemented**:
- **Micro-retro**: Simplify → Quick Learning Check → Iterate Check (with `/clear` suggestion)
- **Phase retro**: Summarize → Learning Review → Backwards Artifact Check →
  Propose Rules Updates → Readiness Gate → Session Hygiene Suggestion

---

## R-005: Rules-Gate CI Implementation

**Decision**: Add the rules-gate as a new job in an existing or dedicated workflow,
using `github.event.pull_request.body` and a `grep` check for the approval reference.

**Rationale**: GitHub Actions can access the PR body via
`github.event.pull_request.body`. A simple `echo "$PR_BODY" | grep -q "Rule-Change-Approval:"`
produces an actionable failure when the reference is missing.

**Trigger**: `pull_request` paths filter on `.agents/rules/base.md`. The job only
runs if that file is in the diff, avoiding noise on unrelated PRs.

**Error message**: The `run` step should exit 1 with an explicit message:
```
ERROR: This PR modifies .agents/rules/base.md.
Add the following line to the PR description before merging:

  Rule-Change-Approval: <link or reference to human approval>

Example: Rule-Change-Approval: https://github.com/owner/repo/issues/42
```

---

## R-006: CODEOWNERS Format

**Decision**: Standard GitHub `CODEOWNERS` format at `.github/CODEOWNERS`.

**Rationale**: Native GitHub feature, no external tooling required. Works with branch
protection rules to auto-request reviewers.

**Pattern**: Each line is `<glob-pattern> @<owner>`. The last matching rule wins for
a given file.

**Minimum required entries** (FR-009):
```
backend/          @<maintainer>
frontend/         @<maintainer>
.github/workflows/ @<maintainer>
.agents/rules/    @<maintainer>
```

---

## Open Items / Resolved Clarifications

| Item | Status | Resolution |
|------|--------|------------|
| `speckit.retro` skill format | ✅ Resolved | File exists; no changes needed |
| GitHub Action SHA for v1.0.70 | ✅ Resolved | `26ec041249acb0a944c0a47b6c0c13f05dbc5b44` |
| Fork PR graceful handling | ✅ Resolved | Repo identity guard on job-level `if` |
| `settings.json` commit policy | ✅ Resolved | Committed; `.local.json` gitignored |
| Rules-gate implementation | ✅ Resolved | `grep` in PR body, job filtered by path |
| CODEOWNERS format | ✅ Resolved | Native GitHub format |
