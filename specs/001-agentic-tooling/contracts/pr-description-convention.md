# Contract: PR Description Convention

**Applies to**: All PRs in this repository
**Version**: 1.0
**Enforced by**: `.github/pull_request_template.md` (template) and
`rules-gate.yml` (CI enforcement for rule changes)

---

## Standard PR Description Format

All PRs MUST use the following structure (pre-populated by the PR template):

```markdown
## Summary

[What the code does now — imperative mood, factual, ≤3 bullet points]

## Validation

- [ ] Tests passed locally
- [ ] Docs updated (if user-facing behavior changed)
- [ ] Frontend client regenerated (if API schema changed)
- [ ] Rule governance: `Rule-Change-Approval: <ref>` added below (if modifying `.agents/rules/base.md`)
```

---

## Rule-Change-Approval Header

**Required when**: The PR diff includes any change to `.agents/rules/base.md`.
**Enforced by**: `rules-gate.yml` CI workflow — PR is blocked if this line is absent.

### Format

```
Rule-Change-Approval: <reference>
```

Where `<reference>` is one of:
- A GitHub issue URL: `https://github.com/owner/repo/issues/42`
- A PR comment URL: `https://github.com/owner/repo/pull/10#issuecomment-12345`
- A discussion reference: `Discussion #7, approved by @maintainer on 2026-03-08`

### Validation Rule

The CI gate checks for the literal prefix `Rule-Change-Approval:` (case-sensitive)
anywhere in the PR body text. It does not validate the content after the colon — any
non-empty reference passes.

### Placement

Place the `Rule-Change-Approval:` line anywhere in the PR body, typically at the
bottom of the Summary section or as a standalone line before the checklist.

### Example PR Body

```markdown
## Summary

- Add rule requiring micro-retro after each implementation task
- Reference speckit.retro.md from the new SpecKit Workflow section

Rule-Change-Approval: https://github.com/owner/repo/issues/8

## Validation

- [x] Tests passed locally
- [x] Docs updated (if user-facing behavior changed)
- [ ] Frontend client regenerated (if API schema changed) — N/A
- [x] Rule governance: Rule-Change-Approval added above
```

---

## What PRs MUST NOT Contain

- Descriptions of discarded approaches or prior iterations
- Time estimates or effort assessments
- Superlatives: "critical", "crucial", "essential", "significant", "comprehensive",
  "robust", "elegant"
- Empty checklist items left unchecked without a reason

---

## Emergency Fixes

If a PR was merged without a `Rule-Change-Approval:` reference (e.g., bypassed
via admin override), the reference MUST be added retroactively to the PR description.
The CI gate can be satisfied on re-run without reopening the PR.
