# AI Feedback Learning Loop

> Documents the process for AI agents to propose rule changes and await human approval. Prevents silent rule drift between sessions.

## When to Propose a Change

Propose a rule change when any of the following happen:

- A human corrects your approach during development and the correction is worth preserving project-wide
- You discover a pattern, constraint, or convention that recurs across multiple tasks and is not yet captured in `.agents/rules/`
- A tool, command, or workflow behaves differently than what the rules describe
- An accepted convention turns out to be incorrect or outdated

Do not propose a change for one-off situations specific to a single task.

## Proposal Format

When you identify a change worth proposing, output the following block in your response:

```
## Rule Change Proposal

**Triggered by**: [What correction or learning surfaced this]
**Proposed rule**: [Exact text to add/change/remove in base.md]
**Section**: [Which section of base.md this belongs in]
**Rationale**: [Why this is worth preserving project-wide]

Awaiting human approval before applying.
```

Include this block in-line in your response — do not create a file or modify any `.agents/rules/` file until the human explicitly approves.

## One-at-a-Time Constraint

Only propose one rule change per session. If multiple corrections surface, log them in `specs/<feature>/lessons-learned.md` and propose them one at a time in future sessions after the current proposal is resolved.

## Human Approval Required

AI agents MUST NOT self-apply rule changes. The rule files in `.agents/rules/` are governance documents — changes require human review and explicit approval. This prevents agents from silently shifting project conventions based on in-session learning that may be wrong or context-specific.

Approval means the human explicitly says something like "approved", "apply it", or "go ahead and update base.md". Implicit agreement or lack of objection is not approval.

## How to Apply After Approval

Once a human explicitly approves a rule change:

1. Open `.agents/rules/base.md` (or the relevant rule file)
2. Apply the exact change described in the proposal — no scope creep
3. Open a PR with the change; include `Rule-Change-Approval: <ref>` in the PR description (reference the conversation, issue, or comment where approval was given)
4. CI will verify the approval reference is present before allowing the merge
