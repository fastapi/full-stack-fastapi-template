---
description: >
  Post-phase retrospective for SpecKit workflows. Run after any SpecKit phase
  (specify, plan, tasks, implement) or after completing a task group. Reviews
  learnings, simplifies generated code, and checks whether earlier artifacts
  need updating before proceeding.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). If the user
provides context (e.g., "after plan phase" or "after task T012"), use it to scope
the review. Otherwise, infer the current phase from available artifacts.

## Outline

There are two retro modes. Run the appropriate one based on context:

- **Micro-retro** — after completing a single task (during `/speckit.implement`)
- **Phase retro** — after completing a full SpecKit phase (specify, plan, tasks,
  implement, or a user story block)

If called standalone (no context), run the **Phase retro**.

---

## Micro-Retro (after a task)

Run this after each completed implementation task before moving to the next one.

### Step 1: Simplify

Re-read the code just written for this task.

- Does any function do more than one thing?
- Is there duplication that could be extracted?
- Are variable and function names self-documenting?
- Is there any dead code, leftover debug output, or commented-out blocks?

Apply fixes immediately if they are small. For larger simplifications, log them
as a follow-up item and continue (do not block progress).

If the `/simplify` skill is available, invoke it on the files touched by this task.

### Step 2: Quick Learning Check

Ask: *Did this task reveal anything unexpected?*

- A constraint not captured in the plan or spec
- A dependency that behaves differently than expected
- A simpler implementation path discovered mid-task
- A requirement that turned out to be ambiguous or wrong

If yes: Add a brief note to `specs/<feature>/lessons-learned.md` (create the file
if it does not exist). Format:

```markdown
## [Task ID] — [Short description]

**What happened**: [One sentence]
**Impact**: [Does this change the plan, spec, or tasks?]
**Proposed action**: [What should change, if anything]
```

If nothing unexpected: proceed immediately.

### Step 3: Iterate Check

Based on what was learned in Step 2, ask:

- Should `tasks.md` be updated? (e.g., a task is now unnecessary, or a new one
  is needed)
- Should `plan.md` be updated? (e.g., a technical decision proved incorrect)
- Should `spec.md` be updated? (e.g., a requirement is now known to be wrong)

**Do not silently update earlier artifacts.** If changes are needed, list them
and ask the user: "I found the following issues — should I update [artifact]?"
Wait for confirmation before changing shared documents.

---

## Phase Retro (after a SpecKit phase)

Run this after completing a full command phase before handing off to the next.

### Step 1: Summarize What Was Produced

State clearly:
- Which phase just completed
- What artifacts were created or updated (file paths)
- Any open items or known gaps

### Step 2: Learning Review

Review `specs/<feature>/lessons-learned.md` (if it exists) and any notes
accumulated during this phase. Then ask:

- What assumptions made at the start of this phase turned out to be wrong?
- What was harder or simpler than expected?
- Did any external constraint (library behavior, API limitation, platform gap)
  surface that is not yet documented?

If there are significant learnings not yet captured, add them to
`specs/<feature>/lessons-learned.md` now.

### Step 3: Backwards Artifact Check

Review earlier artifacts against what was learned. For each artifact, ask the
key question:

| Artifact | Key question |
|----------|-------------|
| `spec.md` | Do any user stories, acceptance scenarios, or requirements need correction? Is the `Status` field current? (Draft → In Progress → Implemented) |
| `plan.md` | Do any technical decisions, constraints, or the project structure need updating? |
| `tasks.md` | Are any tasks now unnecessary, missing, or mis-sequenced? Are all completed tasks marked `[x]`? |
| `constitution.md` | Did this phase reveal a principle violation or gap worth amending? |
| `data-model.md` | Do entities, relationships, or state transitions need correction? |
| `contracts/` | Do any interface contracts need updating? |

For each artifact that needs a change:
1. Describe the change concisely
2. State why (what learning triggered it)
3. Ask the user: "Should I update `[artifact]`?"
4. Wait for confirmation before editing

### Step 4: Propose Constitution or Rules Updates

If this phase revealed a pattern worth enshrining as a project-wide rule
(in `.agents/rules/base.md`), propose it following the AI Feedback Learning Loop
process. Never self-apply — wait for human approval.

### Step 5: Readiness Gate

Confirm before proceeding:

- [ ] lessons-learned.md is up to date (or nothing to add)
- [ ] All earlier artifacts that need updating have been reviewed with the user
- [ ] No open blockers that should prevent the next phase from starting
- [ ] Code simplification applied or deferred with a logged note

If all items are clear, state: "Retro complete — ready for [next phase]."
If any item is blocked, do not proceed until the user resolves it.

### Step 6: Session Hygiene Suggestion

Once the readiness gate is green, suggest a context reset:

> **Good moment to run `/clear`.**
> All state is captured in files — `lessons-learned.md` is up to date, all artifacts
> are current. Starting the next phase with a clean context window will reduce noise
> and keep the agent focused.
>
> When you restart, re-read:
> - `specs/<feature>/plan.md` (or `tasks.md` if moving to implementation)
> - `.agents/rules/base.md`
> - Any artifact updated during this retro

This is a suggestion, not a requirement. If the user prefers to continue without
clearing, proceed. The goal is always the smallest possible context window — suggest
after every task and every phase, regardless of session length.

---

## Output Format

Always produce:

1. A brief **Retro Summary** (3-5 bullet points: what happened, what was learned,
   what changes are proposed)
2. A clear **Ready / Blocked** status
3. If blocked: a numbered list of specific actions the user needs to take
4. If ready: the session hygiene suggestion (Step 6)
