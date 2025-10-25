---
name: pr-labeling
description: MUST activate whenever creating a pull request. Automatically applies labels based on conventional commit types to pass check-labels workflow. Use proactively - do not wait for user to ask.
allowed-tools: Bash, Read, Grep
---

# Pull Request Auto-Labeling

## Activation

**MANDATORY activation whenever:**
- Creating a pull request (gh pr create, any PR creation)
- User says "create pr", "open pr", "make a pull request"
- Discussing or reviewing pull requests
- After pushing commits when PR creation is next step

**Proactive**: Apply labels automatically without waiting for user to ask.

## Core Function

1. **Detect commit type** from PR title, branch name, or commits
2. **Map to label** using table below
3. **Apply label** via `gh pr create --label` or `gh pr edit --add-label`

## Label Mapping

| Commit Type | Label | Notes |
|-------------|-------|-------|
| `feat` | `feature` | New features |
| `fix` | `bug` | Bug fixes |
| `docs` | `docs` | Documentation |
| `refactor` | `refactor` | Code refactoring |
| `perf` | `enhancement` | Performance |
| `test` | `feature` | Tests |
| `chore` | `internal` | Maintenance |
| `ci` | `internal` | CI/CD |
| `style` | `internal` | Formatting |
| `build` | `internal` | Build system |
| `feat!` / `fix!` | `feature` / `bug` + `breaking` | Breaking changes |

**Special labels** (add when applicable):
- `security` - Security-related changes
- `upgrade` - Dependency upgrades
- `breaking` - Breaking changes (feat!, fix!, or BREAKING CHANGE in body)

## Detection Priority

1. PR title (e.g., `feat(auth): add OAuth2`)
2. Branch name (e.g., `feature/CUR-30-description`)
3. Dominant commit type in branch

## Commands

**Create PR with label:**
```bash
gh pr create --label "feature" --title "..." --body "..."
```

**Add label to existing PR:**
```bash
gh pr edit <pr-number> --add-label "feature"
```

**Multiple labels:**
```bash
gh pr create --label "feature" --label "breaking" ...
gh pr edit <pr-number> --add-label "feature,breaking"
```

**Verify labels:**
```bash
gh pr view <pr-number> --json labels --jq '.labels[].name'
```

## Workflow

**When creating PR:**
1. Analyze PR title for conventional commit type
2. Determine primary label from mapping table
3. Check for breaking changes (add `breaking` if found)
4. Check for security keywords (add `security` if found)
5. Apply labels: `gh pr create --label "primary" [--label "secondary"] ...`

**For existing unlabeled PR:**
1. Fetch PR details: `gh pr view <pr-number>`
2. Analyze title and commits
3. Apply labels: `gh pr edit <pr-number> --add-label "primary[,secondary]"`

## Requirements

- At least **one type label** required (check-labels workflow enforces this)
- Labels must exist in repository (verify with `gh label list`)
- Use lowercase label names
- Multiple labels OK when PR spans types

## Examples

```bash
# Feature PR
Title: "feat(storage): enhance Supabase Storage"
→ gh pr create --label "feature" ...

# Bug fix PR
Title: "fix(api): resolve timeout issues"
→ gh pr create --label "bug" ...

# Breaking change
Title: "feat!: redesign auth API"
→ gh pr create --label "feature" --label "breaking" ...

# Documentation
Title: "docs(readme): update setup guide"
→ gh pr create --label "docs" ...

# Internal maintenance
Title: "chore(deps): upgrade FastAPI"
→ gh pr create --label "internal" --label "upgrade" ...
```

---

<!-- Version: v2 - Simplified: 2025-10-25 -->
