---
name: pr-labeling
description: Automatically labels pull requests based on conventional commit types to ensure they pass check-labels workflows. Activates when creating PRs, discussing pull requests, or when user mentions "pull request", "PR", "create pr", "label pr", or git workflows involving PRs.
allowed-tools: Bash, Read, Grep
---

# Pull Request Auto-Labeling

## Purpose

This skill ensures all pull requests are properly labeled based on conventional commit types, enabling them to pass automated check-labels workflows and providing visual organization for PR reviews. Labels are automatically determined from PR title, branch name, and commit messages.

## When This Skill Activates

**Automatically triggers when:**
- Creating a pull request (gh pr create, /create-pr commands)
- After pushing commits and discussing PR creation
- Reviewing or discussing pull requests
- User mentions "pull request", "PR", "create pr", "open pr"
- User mentions "label", "label pr", "add labels"
- Discussing GitHub workflows or PR requirements
- Troubleshooting check-labels workflow failures

**Also activates for:**
- PR review and organization tasks
- Ensuring PRs meet workflow requirements
- Bulk PR labeling operations
- Setting up PR automation

## Label Mapping

Labels are automatically determined based on conventional commit type from PR title or branch name:

| Commit Type | Label | Description | Example |
|-------------|-------|-------------|---------|
| `feat` | `feature` | New feature implementation | feat(auth): add OAuth2 support |
| `fix` | `bug` | Bug fixes | fix(api): resolve rate limiting |
| `docs` | `docs` | Documentation changes | docs(readme): update setup guide |
| `refactor` | `refactor` | Code refactoring | refactor(storage): improve error handling |
| `test` | `feature` | Test additions | test(auth): add unit tests |
| `chore` | `internal` | Maintenance tasks | chore(deps): update packages |
| `ci` | `internal` | CI/CD changes | ci(github): add workflow |
| `perf` | `enhancement` | Performance improvements | perf(api): optimize queries |
| `style` | `internal` | Code style changes | style(lint): fix formatting |
| `build` | `internal` | Build system changes | build(docker): update image |
| `revert` | `bug` | Revert changes | revert: previous commit |
| `breaking` | `breaking` | Breaking changes | feat!: new API format |

## Automatic Label Detection

The skill analyzes multiple sources to determine the correct label:

### Priority Order:
1. **PR Title** - Extract conventional commit type from title
2. **Branch Name** - Parse type from branch name (e.g., `feature/CUR-30-description`)
3. **Commit Messages** - Analyze commits for dominant type
4. **BREAKING CHANGE** - Check for breaking change markers (adds `breaking` label)

### Detection Patterns:

**From PR Title:**
```
feat(auth): add OAuth2 support           → feature
fix(api): resolve timeout issues         → bug
docs(readme): update installation        → docs
refactor(storage): improve structure     → refactor
perf(queries): optimize database calls   → enhancement
```

**From Branch Name:**
```
feature/CUR-30-oauth-integration        → feature
fix/CUR-45-rate-limiting                → bug
docs/CUR-50-api-documentation           → docs
refactor/CUR-55-code-cleanup            → refactor
chore/CUR-60-dependency-update          → internal
```

**Breaking Changes:**
```
feat!: new API format                    → feature + breaking
feat(api)!: change endpoint structure    → feature + breaking
BREAKING CHANGE: in commit body          → breaking (added)
```

## Workflow Integration

### When Creating a PR

**Scenario 1: User creates PR with gh pr create**
```bash
User: "gh pr create --title 'feat(storage): enhance Supabase Storage service'"
Skill activates:
1. Detects type: "feat" → label: "feature"
2. Adds --label "feature" to command
3. Checks for breaking changes → none found
4. Confirms: "✓ PR created with label: feature"
```

**Scenario 2: User asks to create PR**
```
User: "create a pull request for this storage enhancement"
Skill activates:
1. Analyzes recent commits for type
2. Checks current branch name
3. Determines label(s) needed
4. Creates PR with appropriate labels
5. Confirms labels applied
```

**Scenario 3: Multiple commit types**
```
User: "create PR for this feature with bug fixes"
Skill activates:
1. Detects multiple types: feat + fix
2. Primary label: "feature" (feat takes priority)
3. Secondary label: "bug" (if significant fixes)
4. Creates PR: gh pr create --label "feature" --label "bug"
```

### After PR Creation

**Scenario 4: PR created without labels**
```bash
User: "I created PR #3 but forgot to add labels"
Skill activates:
1. Fetches PR details: gh pr view 3
2. Analyzes PR title and commits
3. Determines correct labels
4. Applies labels: gh pr edit 3 --add-label "feature"
5. Confirms: "✓ Added labels: feature"
```

## Label Application Commands

### Via gh CLI:

**Create PR with labels:**
```bash
gh pr create --title "feat(auth): add OAuth2" --label "feature" --body "..."
```

**Add labels to existing PR:**
```bash
gh pr edit <pr-number> --add-label "feature"
gh pr edit <pr-number> --add-label "feature,breaking"  # Multiple labels
```

**Check PR labels:**
```bash
gh pr view <pr-number> --json labels
```

### Label Validation:

Before applying labels, verify they exist in the repository:
```bash
gh label list | grep -i "feature"
```

## Check-Labels Workflow

This skill ensures PRs meet check-labels workflow requirements:

### Typical Check-Labels Requirements:
- At least one type label (feature, bug, docs, etc.)
- Breaking change label if applicable
- Size labels (optional): S, M, L, XL
- Status labels (optional): needs-review, approved

### Validation Steps:
1. ✓ PR has at least one type label
2. ✓ Label matches PR content type
3. ✓ Breaking changes are marked
4. ✓ Labels are valid (exist in repository)

### Failure Scenarios:

**No labels:**
```
❌ check-labels: FAILED
   PR must have at least one label

Skill activates: "Let me add the appropriate label based on your PR title/commits"
```

**Invalid label:**
```
❌ check-labels: FAILED
   Label 'features' does not exist (did you mean 'feature'?)

Skill activates: "Correcting label to 'feature'"
```

**Missing breaking change label:**
```
❌ check-labels: FAILED
   PR contains breaking changes but missing 'breaking' label

Skill activates: "Adding 'breaking' label due to BREAKING CHANGE in commits"
```

## Multiple Label Scenarios

### Feature with Breaking Change:
```
Type: feat!
Labels: feature, breaking

Command: gh pr create --label "feature" --label "breaking"
```

### Feature with Documentation:
```
Types: feat + docs (significant docs)
Labels: feature, docs

Command: gh pr create --label "feature" --label "docs"
```

### Bug Fix with Security:
```
Type: fix (security vulnerability)
Labels: bug, security

Command: gh pr create --label "bug" --label "security"
```

### Dependency Upgrade:
```
Type: chore (dependency upgrade)
Labels: internal, upgrade

Command: gh pr create --label "internal" --label "upgrade"
```

## Repository Label Standards

### Required Labels (from repository):
- `feature` - New feature implementation (#0e8a16)
- `bug` - Something isn't working (#d73a4a)
- `docs` - Documentation changes (#0075ca)
- `refactor` - Code refactoring (#fbca04)
- `breaking` - Breaking change (#d73a4a)
- `enhancement` - New feature or request (#a2eeef)
- `internal` - Internal changes (#ffffff)
- `security` - Security-related changes (#ee0701)
- `upgrade` - Dependency upgrades (#0052cc)

### Creating Missing Labels:

If a required label doesn't exist, create it:
```bash
gh label create "feature" --description "New feature implementation" --color "0e8a16"
```

## Integration with Other Skills

**Works with:**
- `commit-messages`: Uses same conventional commit types for consistency
- `tdd-workflow`: Test PRs automatically labeled as "feature" or "enhancement"
- `api-contract-first`: API PRs get "feature" or "breaking" labels
- Linear integration: Syncs PR labels with Linear issue labels

## Best Practices

### DO:
- ✓ Apply labels immediately when creating PRs
- ✓ Use consistent conventional commit types
- ✓ Add "breaking" label for breaking changes
- ✓ Include "security" label for security fixes
- ✓ Verify labels match PR content
- ✓ Add multiple labels if PR spans multiple types

### DON'T:
- ✗ Create PRs without labels (check-labels will fail)
- ✗ Use non-existent labels
- ✗ Mislabel PR type (confuses reviewers)
- ✗ Forget "breaking" label for breaking changes
- ✗ Mix too many types in one PR (split if needed)

## Examples

### Example 1: Feature PR
```bash
Branch: feature/CUR-30-storage-enhancement
Title: feat(storage): enhance Supabase Storage service with security

Skill action:
- Detects type: feat → feature
- Command: gh pr create --label "feature" --title "..." --body "..."
- Result: ✓ PR #2 created with labels: feature
```

### Example 2: Bug Fix PR
```bash
Branch: fix/CUR-45-rate-limiting-bug
Title: fix(api): resolve rate limiting on user endpoint

Skill action:
- Detects type: fix → bug
- Command: gh pr create --label "bug" --title "..." --body "..."
- Result: ✓ PR created with labels: bug
```

### Example 3: Breaking Change PR
```bash
Title: feat!: redesign authentication API
Commits contain: "BREAKING CHANGE: new auth flow"

Skill action:
- Detects type: feat! → feature + breaking
- Command: gh pr create --label "feature" --label "breaking" --title "..." --body "..."
- Result: ✓ PR created with labels: feature, breaking
```

### Example 4: Documentation PR
```bash
Branch: docs/CUR-50-api-documentation
Title: docs(api): add comprehensive API documentation

Skill action:
- Detects type: docs → docs
- Command: gh pr create --label "docs" --title "..." --body "..."
- Result: ✓ PR created with labels: docs
```

### Example 5: Existing PR Without Labels
```bash
User: "PR #3 is missing labels, can you add them?"

Skill action:
1. Fetch PR: gh pr view 3
2. Analyze title: "refactor(storage): improve error handling"
3. Detect type: refactor → refactor
4. Apply label: gh pr edit 3 --add-label "refactor"
5. Result: ✓ Added labels to PR #3: refactor
```

### Example 6: Multiple Types
```bash
Title: feat(auth): add OAuth2 with bug fixes
Commits: 3 feat commits, 2 fix commits

Skill action:
- Primary type: feat → feature
- Secondary type: fix → bug (significant)
- Command: gh pr create --label "feature" --label "bug" --title "..." --body "..."
- Result: ✓ PR created with labels: feature, bug
```

## Validation Checklist

Before creating PR, verify:
- [ ] PR title follows conventional commit format
- [ ] Branch name includes type prefix or story ID
- [ ] At least one type label determined
- [ ] Breaking changes marked with "breaking" label
- [ ] Security fixes marked with "security" label
- [ ] Labels exist in repository
- [ ] Multiple labels added if PR spans types

## Troubleshooting

### Check-Labels Workflow Fails

**Problem:** PR created without labels
```bash
Solution:
1. Identify PR type from title/commits
2. Apply appropriate label: gh pr edit <pr-number> --add-label "<label>"
3. Verify: gh pr view <pr-number> --json labels
4. Re-run check-labels workflow if needed
```

**Problem:** Label doesn't exist
```bash
Solution:
1. Check available labels: gh label list
2. Create missing label: gh label create "<name>" --description "..." --color "..."
3. Apply to PR: gh pr edit <pr-number> --add-label "<label>"
```

**Problem:** Wrong label applied
```bash
Solution:
1. Remove wrong label: gh pr edit <pr-number> --remove-label "wrong-label"
2. Add correct label: gh pr edit <pr-number> --add-label "correct-label"
3. Verify: gh pr view <pr-number> --json labels
```

## Quick Reference

**Label mapping:**
- feat → feature
- fix → bug
- docs → docs
- refactor → refactor
- test → feature
- chore → internal
- ci → internal
- perf → enhancement
- breaking → breaking (additional)

**Create PR with labels:**
```bash
gh pr create --label "feature" --title "feat(scope): description" --body "..."
```

**Add labels to existing PR:**
```bash
gh pr edit <pr-number> --add-label "feature"
gh pr edit <pr-number> --add-label "feature,breaking"
```

**Check PR labels:**
```bash
gh pr view <pr-number> --json labels
```

**List available labels:**
```bash
gh label list
```

## Notes

- **Automatic activation**: Triggers when creating or discussing PRs
- **Label requirement**: At least one type label required for check-labels workflow
- **Breaking changes**: Always add "breaking" label for feat!, fix!, etc.
- **Multiple labels**: OK to have multiple labels if PR spans types
- **Case sensitivity**: Label names are case-sensitive, use lowercase
- **gh CLI integration**: Skill uses gh CLI commands for all operations
- **Validation**: Verifies labels exist before applying
- **Consistency**: Aligns with commit-messages skill for conventional commit types
- **Priority**: feat > fix > docs > others when multiple types present
- **Security**: Always add "security" label for security-related changes
- **Upgrades**: Add "upgrade" label for dependency updates
- **Linear sync**: Labels can sync with Linear issue labels

---

<!-- Version: v1 - Created: 2025-10-25 -->
