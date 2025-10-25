# PR Labeling Reference

## GitHub Labels in Repository

Current labels available (from `gh label list`):

| Label | Description | Color | Usage |
|-------|-------------|-------|-------|
| `bug` | Something isn't working | #d73a4a | Bug fixes (fix type) |
| `documentation` | Improvements or additions to documentation | #0075ca | Legacy docs label |
| `docs` | Documentation changes | #0075ca | Documentation (docs type) |
| `duplicate` | This issue or pull request already exists | #cfd3d7 | Duplicate items |
| `enhancement` | New feature or request | #a2eeef | Enhancements (perf type) |
| `feature` | New feature implementation | #0e8a16 | Features (feat type) |
| `good first issue` | Good for newcomers | #7057ff | Beginner-friendly |
| `help wanted` | Extra attention is needed | #008672 | Community help |
| `invalid` | This doesn't seem right | #e4e669 | Invalid items |
| `question` | Further information is requested | #d876e3 | Questions |
| `wontfix` | This will not be worked on | #ffffff | Won't fix |
| `breaking` | Breaking change | #d73a4a | Breaking changes |
| `refactor` | Code refactoring | #fbca04 | Refactoring |
| `security` | Security-related changes | #ee0701 | Security fixes |
| `upgrade` | Dependency upgrades | #0052cc | Dependency updates |
| `internal` | Internal changes | #ffffff | Internal/chore changes |
| `lang-all` | Language changes affecting all | #bfdadc | i18n changes |

## Conventional Commit Type to Label Mapping

```yaml
feat: feature
fix: bug
docs: docs
refactor: refactor
test: feature
chore: internal
ci: internal
perf: enhancement
style: internal
build: internal
revert: bug
breaking: breaking  # Additional label
```

## Label Priority (When Multiple Types Present)

1. **feat** → feature (highest priority)
2. **fix** → bug
3. **docs** → docs
4. **refactor** → refactor
5. **perf** → enhancement
6. **test** → feature
7. **chore** → internal (lowest priority)

**Special:**
- **breaking** → Always added as additional label when detected
- **security** → Always added for security-related changes
- **upgrade** → Always added for dependency updates

## gh CLI Commands Reference

### Create PR with Labels

```bash
# Single label
gh pr create --label "feature" --title "feat(auth): add OAuth2" --body "..."

# Multiple labels
gh pr create --label "feature" --label "breaking" --title "feat!: new API" --body "..."

# With all options
gh pr create \
  --title "feat(storage): enhance Supabase Storage service" \
  --body "$(cat pr-body.md)" \
  --label "feature" \
  --label "security"
```

### Edit Existing PR

```bash
# Add single label
gh pr edit 2 --add-label "feature"

# Add multiple labels
gh pr edit 2 --add-label "feature,breaking"

# Remove label
gh pr edit 2 --remove-label "wrong-label"

# Replace all labels
gh pr edit 2 --add-label "feature,docs" --remove-label "bug"
```

### View PR Labels

```bash
# View all PR details including labels
gh pr view 2

# View only labels (JSON)
gh pr view 2 --json labels

# View labels formatted
gh pr view 2 --json labels --jq '.labels[].name'
```

### List All Labels in Repository

```bash
# List all labels
gh label list

# Search for specific label
gh label list | grep -i "feature"

# Get label details
gh label list --json name,description,color
```

### Create New Labels

```bash
# Create label
gh label create "feature" \
  --description "New feature implementation" \
  --color "0e8a16"

# Create multiple labels
gh label create "breaking" --description "Breaking change" --color "d73a4a"
gh label create "security" --description "Security-related changes" --color "ee0701"
```

## Breaking Change Detection Patterns

### In PR Title:
```
feat!: new API format                     → breaking
feat(api)!: change endpoint structure     → breaking
fix!: update authentication flow          → breaking
```

### In Commit Messages:
```
BREAKING CHANGE: removed legacy API       → breaking
BREAKING CHANGES: new auth flow           → breaking

feat(api): add new endpoint

BREAKING CHANGE: endpoints now use v2     → breaking
```

### In PR Body:
```markdown
## Breaking Changes

- Removed `/v1/` endpoints
- Changed authentication flow
```

## Example PR Creation Scenarios

### Scenario 1: Simple Feature
```bash
Title: feat(auth): add OAuth2 support
Type: feat
Labels: feature

Command:
gh pr create --label "feature" --title "feat(auth): add OAuth2 support"
```

### Scenario 2: Bug Fix
```bash
Title: fix(api): resolve rate limiting bug
Type: fix
Labels: bug

Command:
gh pr create --label "bug" --title "fix(api): resolve rate limiting bug"
```

### Scenario 3: Breaking Feature
```bash
Title: feat!: redesign authentication API
Type: feat! (breaking)
Labels: feature, breaking

Command:
gh pr create --label "feature" --label "breaking" --title "feat!: redesign authentication API"
```

### Scenario 4: Security Fix
```bash
Title: fix(security): patch SQL injection vulnerability
Type: fix (security)
Labels: bug, security

Command:
gh pr create --label "bug" --label "security" --title "fix(security): patch SQL injection vulnerability"
```

### Scenario 5: Documentation
```bash
Title: docs(readme): update installation guide
Type: docs
Labels: docs

Command:
gh pr create --label "docs" --title "docs(readme): update installation guide"
```

### Scenario 6: Refactoring
```bash
Title: refactor(storage): improve error handling
Type: refactor
Labels: refactor

Command:
gh pr create --label "refactor" --title "refactor(storage): improve error handling"
```

### Scenario 7: Dependency Upgrade
```bash
Title: chore(deps): upgrade FastAPI to 0.115.0
Type: chore (upgrade)
Labels: internal, upgrade

Command:
gh pr create --label "internal" --label "upgrade" --title "chore(deps): upgrade FastAPI to 0.115.0"
```

### Scenario 8: Multiple Types
```bash
Title: feat(auth): add OAuth2 with bug fixes
Commits: 3 feat, 2 fix
Labels: feature, bug

Command:
gh pr create --label "feature" --label "bug" --title "feat(auth): add OAuth2 with bug fixes"
```

## Check-Labels Workflow Template

If you need to create a check-labels workflow, here's a template:

```yaml
# .github/workflows/check-labels.yml
name: Check PR Labels

on:
  pull_request:
    types: [opened, labeled, unlabeled, synchronize]

jobs:
  check-labels:
    runs-on: ubuntu-latest
    steps:
      - name: Check for required labels
        uses: mheap/github-action-required-labels@v5
        with:
          mode: exactly
          count: 1
          labels: "feature, bug, docs, refactor, enhancement, internal, breaking, security, upgrade"
          add_comment: true
```

## Label Validation Script

Python script to validate PR labels (can be used in CI):

```python
#!/usr/bin/env python3
import json
import subprocess
import sys

REQUIRED_LABELS = [
    "feature", "bug", "docs", "refactor",
    "enhancement", "internal", "breaking",
    "security", "upgrade"
]

def check_pr_labels(pr_number):
    """Check if PR has at least one required label."""
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "labels"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to fetch PR #{pr_number}")
        return False

    data = json.loads(result.stdout)
    labels = [label["name"] for label in data.get("labels", [])]

    if not labels:
        print(f"❌ PR #{pr_number} has no labels")
        return False

    has_required = any(label in REQUIRED_LABELS for label in labels)

    if not has_required:
        print(f"❌ PR #{pr_number} missing required labels")
        print(f"   Current labels: {', '.join(labels)}")
        print(f"   Required labels: {', '.join(REQUIRED_LABELS)}")
        return False

    print(f"✓ PR #{pr_number} has valid labels: {', '.join(labels)}")
    return True

if __name__ == "__main__":
    pr_number = sys.argv[1] if len(sys.argv) > 1 else None
    if not pr_number:
        print("Usage: check_labels.py <pr_number>")
        sys.exit(1)

    success = check_pr_labels(pr_number)
    sys.exit(0 if success else 1)
```

## Troubleshooting Common Issues

### Issue: Label doesn't exist
```bash
Error: label "features" not found

Solution:
1. Check available labels: gh label list
2. Use correct label name: "feature" (not "features")
3. Or create the label: gh label create "features" --description "..." --color "..."
```

### Issue: Can't add label to PR
```bash
Error: must have admin, write, or triage access

Solution:
1. Ensure you have write access to repository
2. Check if PR is from fork (limited label permissions)
3. Contact repository maintainer for access
```

### Issue: Multiple labels not applying
```bash
Command: gh pr edit 2 --add-label "feature, breaking"
Error: label "feature, breaking" not found

Solution:
Remove space after comma:
gh pr edit 2 --add-label "feature,breaking"
```

### Issue: Check-labels workflow still failing
```bash
Problem: Added label but workflow still fails

Solution:
1. Verify label was added: gh pr view <pr> --json labels
2. Re-run workflow: gh run rerun <run-id>
3. Check workflow requirements match actual labels
4. Check for typos in label names (case-sensitive)
```

## Best Practices Summary

1. **Always label PRs immediately** when creating them
2. **Use conventional commit types** in PR titles
3. **Add breaking label** for any breaking changes
4. **Add security label** for security-related fixes
5. **Add multiple labels** when PR spans multiple types
6. **Validate labels exist** before applying
7. **Keep labels consistent** with commit message types
8. **Document label meanings** for team clarity
9. **Automate where possible** using GitHub Actions
10. **Review labels** during PR review process

## Integration with Linear

If using Linear integration, labels can sync with Linear issue labels:

```yaml
# Linear → GitHub Label Sync
Epic → internal
Story → feature/bug/docs (based on type)
Task → Same as parent story

# Example:
Linear Story (type: Feature) → GitHub PR label: feature
Linear Story (type: Bug) → GitHub PR label: bug
Linear Epic → GitHub PR label: internal
```

---

**Updated:** 2025-10-25
**Maintainer:** Aygentic
