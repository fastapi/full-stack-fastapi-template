# Feature Specification: Agentic Development Infrastructure

**Feature Branch**: `001-agentic-tooling`
**Created**: 2026-03-08
**Status**: Implemented
**Input**: Apply colombia-data-jobs agentic development learnings — agent rules, AI feedback
loop, Claude CI workflows, PR governance, tool permissions, and testing/pipeline improvements.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Onboards Without Repeated Corrections (Priority: P1)

An AI coding assistant opens this project for the first time and can immediately understand
the architecture, conventions, commands, and quality standards by reading structured rule
files in `.agents/rules/`. When the agent makes a mistake, a documented feedback loop lets
the correction become a durable project rule rather than being lost between sessions. The
agent never has to ask basic questions ("how do I run tests?", "what is the project
structure?") after the first session.

**Why this priority**: Without this, every new AI session starts blind. The agent wastes
time asking basic questions, makes repeated mistakes, and has no mechanism to improve
project-wide conventions over time. This is the foundation for all other agentic work.

**Independent Test**: Open a new Claude Code session on a fresh clone, point it at the
project, and verify the agent can describe the full-stack architecture, execute the correct
test commands, and propose a rule change following the documented process — without being
prompted.

**Acceptance Scenarios**:

1. **Given** a new AI session with no prior context, **When** the agent reads
   `.agents/rules/`, **Then** it correctly identifies the backend stack, frontend stack,
   available test commands, and deployment workflow.
2. **Given** a human corrects the AI's approach during development, **When** the correction
   is a pattern worth preserving, **Then** the AI proposes a structured rule change (without
   self-applying it) and explicitly awaits human approval.
3. **Given** an approved rule change, **When** the AI updates the rules file, **Then** all
   future sessions inherit the correction and the prior mistake does not repeat.

---

### User Story 2 - Pull Requests Receive Automated AI Code Review (Priority: P2)

When a developer opens a PR that changes backend, frontend, or CI workflow code, an AI
reviewer automatically posts a structured code review before any human sees the PR. The
reviewer surfaces issues — missing tests, security concerns, style violations, logic errors
— immediately after the PR is opened or updated.

Additionally, team members can mention `@claude` in any PR comment or GitHub issue to
invoke Claude directly: answering questions, explaining code, creating fixes.

**Why this priority**: Automated AI review catches issues earlier and reduces the review
burden on maintainers. Contributors get immediate feedback without waiting for human
availability. The `@claude` trigger makes the AI an active participant in development
discussions.

**Independent Test**: Open a PR with a deliberate issue (e.g., hardcoded credential, missing
test) → verify Claude posts a review comment identifying the issue within 5 minutes of
opening. Separately, post `@claude explain this function` in a PR comment and verify a
response appears.

**Acceptance Scenarios**:

1. **Given** a PR modifying Python or TypeScript source files is opened or updated, **When**
   CI runs, **Then** Claude posts a review with specific file:line observations.
2. **Given** a comment containing `@claude` is posted on a PR or issue, **When** submitted,
   **Then** Claude takes the requested action and responds in the same thread.
3. **Given** a PR that only changes documentation files, **When** CI runs, **Then** the AI
   code review step is skipped to avoid noise and unnecessary cost.

---

### User Story 3 - Project Governance Prevents Rule Drift (Priority: P3)

The agent rules file — the source of truth for AI agent behavior — is protected from
accidental modification. If any PR modifies this file, the CI pipeline requires an explicit
approval reference in the PR description. A standardized PR template ensures all contributors
document validation steps before merging. CODEOWNERS ensures critical areas of the codebase
always get reviewed by the right people.

**Why this priority**: Without protection, AI agents can silently alter their own rules
across sessions, and rule changes can be merged without traceability. The AI feedback loop
only works if rule changes are deliberate, documented, and human-approved.

**Independent Test**: Open a PR that modifies `.agents/rules/base.md` without adding
`Rule-Change-Approval: <reference>` in the PR body → CI fails with a clear, actionable
error message explaining exactly what to add.

**Acceptance Scenarios**:

1. **Given** a PR modifies the rules file without an approval reference, **When** CI runs,
   **Then** the job fails and the error message instructs the developer to add
   `Rule-Change-Approval: <link-or-reference>` to the PR description.
2. **Given** a PR modifies the rules file WITH a valid approval reference, **When** CI runs,
   **Then** the rules-file gate passes and does not block the PR.
3. **Given** a new contributor opens a PR, **When** they see the PR template, **Then** they
   find a pre-populated checklist (tests passed, docs updated, rule governance reference)
   that reduces back-and-forth with maintainers.
4. **Given** CODEOWNERS is configured, **When** a PR touches backend, frontend, or CI
   workflows, **Then** the designated maintainers are automatically requested as reviewers.

---

### User Story 4 - Claude Tool Permissions Pre-Configured for Safe Development (Priority: P4)

When any team member opens this project in Claude Code, the tool permissions are already
configured: running tests, running linters, checking Docker status, and read-only git
operations are all pre-approved and require no manual confirmation. Destructive or
externally-visible operations (force pushes, dropping databases, pushing to remote) still
require explicit human approval.

**Why this priority**: Without a shared permissions baseline, each developer must manually
allow tools or operate in fully-manual mode. This creates inconsistent AI behaviors across
the team and slows down agentic workflows.

**Independent Test**: Clone the project, open Claude Code, and verify that test and lint
commands execute without permission prompts, while destructive git operations prompt for
confirmation.

**Acceptance Scenarios**:

1. **Given** a developer opens the project in Claude Code, **When** Claude attempts to run
   backend tests or frontend linters, **Then** it proceeds without prompting for approval.
2. **Given** a developer opens the project, **When** Claude attempts a destructive operation
   (force push, database drop, hard reset), **Then** it requires explicit human confirmation.
3. **Given** the permissions file is committed to the repository, **When** any team member
   opens the project in Claude Code, **Then** they have the same baseline permission set
   without additional manual setup.

---

### User Story 5 - SpecKit Phases Are Followed by Structured Retrospectives (Priority: P5)

Every SpecKit phase (specify, plan, tasks, implement) ends with a mandatory retrospective
before the next phase begins. After each implementation task, the AI simplifies the code
just written, logs any unexpected learnings, and checks whether earlier artifacts need
correction. After each full phase, the AI reviews accumulated learnings, proposes updates
to earlier documents, and confirms nothing is blocking the next phase.

A `/speckit.retro` skill is available for the team to invoke explicitly at any time — for
example, after a mid-session interruption, or to run a standalone retrospective on a
completed feature. The retro behavior is enforced via `.agents/rules/base.md` (not by
modifying SpecKit's own command files), so it works in any project that has `base.md`
and the `speckit.retro` skill, and survives SpecKit updates without conflict.

After every retro gate passes, the agent suggests running `/clear` to start the next
task or phase with a minimal context window, stating exactly which files to re-read
after the reset.

**Why this priority**: Without retrospective checkpoints, technical debt accumulates
silently across tasks. Assumptions made during specification turn out to be wrong but
are never corrected. Plans become stale. The cost of divergence compounds: fixing a
wrong requirement after implementation costs ten times more than fixing it at the spec
stage. Structured retrospectives keep all artifacts in sync with reality throughout
the workflow. The session hygiene suggestion compounds this: a smaller context window
means a more focused, cheaper, and less error-prone agent at every step.

**Independent Test**: With `base.md` in place, start a new SpecKit workflow. After
each phase completes, verify the agent pauses, runs the retro, and suggests `/clear`
with specific re-read instructions before proceeding. Verify the agent never silently
edits an earlier artifact as a result of a later-phase learning.

**Acceptance Scenarios**:

1. **Given** a SpecKit phase completes (specify, plan, tasks, or an implement phase
   boundary), **When** the agent prepares to hand off to the next phase, **Then** it
   runs `/speckit.retro` in phase-retro mode: summarizes output, reviews learnings,
   checks earlier artifacts, and produces a Ready/Blocked status.
2. **Given** a task completes during `/speckit.implement`, **When** the agent marks
   it `[X]`, **Then** it runs `/speckit.retro` in micro-retro mode: simplifies code,
   logs learnings, checks for artifact drift — then suggests `/clear` before the next
   task.
3. **Given** a developer runs `/speckit.retro` manually at any point, **When** invoked,
   **Then** it produces a Retro Summary, a Ready/Blocked status, and a session hygiene
   suggestion naming the exact files to re-read after `/clear`.
4. **Given** a learning surfaces in any phase that contradicts an earlier artifact,
   **When** the agent identifies the discrepancy, **Then** it proposes the update and
   awaits human approval — it never silently overwrites earlier documents.
5. **Given** the retro gate is green, **When** the agent produces its final output,
   **Then** it always includes the session hygiene suggestion with the specific files
   to re-read, regardless of session length.

---

### Edge Cases

- What if a fork PR opens the Claude review workflow without access to secrets? The
  workflow must detect missing credentials and skip gracefully instead of failing loudly.
- What if an AI agent proposes conflicting rule changes in rapid succession? The
  one-change-at-a-time constraint documented in the feedback loop prevents accumulation of
  unapproved changes.
- What if `@claude` is mentioned in an unrelated comment (spam, off-topic)? Claude responds
  scoped to the PR/issue context and does not take action outside that scope.
- What if the rules file gate blocks an emergency fix? The approval reference can be added
  retroactively to the PR description without reopening the PR.
- What if the micro-retro finds a simplification that requires touching many files? The
  agent logs it as a follow-up item and continues — it does not block task progress for
  large refactors discovered mid-implementation.
- What if `/speckit.retro` is invoked with no feature context (no `specs/` directory)?
  It MUST fail gracefully with a clear message rather than silently doing nothing.
- What if a phase retro finds that the spec was fundamentally wrong? The agent proposes
  stopping implementation, correcting the spec with human approval, and re-running
  `/speckit.tasks` — it does not patch the implementation around a wrong requirement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST contain `.agents/rules/base.md` with the project overview,
  architecture, stack, available commands, testing conventions, SDD workflow, and project
  rules.
- **FR-002**: Repository MUST contain `.agents/rules/ai-feedback-learning-loop.md`
  documenting the process for AI agents to propose rule changes and await human approval
  before applying them.
- **FR-003**: Repository MUST contain `.agents/rules/coding-standards.md` capturing
  agreed-upon code quality standards (SOLID, Clean Code, naming, testing conventions).
- **FR-004**: `CLAUDE.md` in the repository root MUST reference `.agents/rules/base.md` as
  the single source of truth for agent conventions. Symlinks or re-exports for `AGENTS.md`
  and `GEMINI.md` are optional but recommended.
- **FR-005**: A CI workflow MUST automatically trigger an AI code review on every PR that
  modifies source code files (backend, frontend, CI configuration). It MUST skip docs-only
  PRs.
- **FR-006**: A CI workflow MUST listen for `@claude` mentions in PR comments, PR review
  comments, and GitHub issues, and invoke Claude Code to respond and take action.
- **FR-007**: The existing CI pipeline MUST include a gate that blocks any PR modifying
  `.agents/rules/base.md` if the PR description does not contain a
  `Rule-Change-Approval: <reference>` line.
- **FR-008**: A pull request template MUST be present at `.github/pull_request_template.md`
  with a summary section and a validation checklist (tests run, docs updated if needed,
  rule governance reference).
- **FR-009**: `.github/CODEOWNERS` MUST define ownership for at least the backend, frontend,
  and CI workflow directories.
- **FR-010**: `.claude/settings.json` MUST pre-approve tool permissions for common
  development operations: running tests, running linters, docker compose operations, and
  read-only git commands. Destructive operations MUST remain on explicit approval.
- **FR-011**: A `/speckit.retro` skill MUST exist defining two retrospective modes:
  a **micro-retro** (after each task: simplify code, log learnings, check for artifact
  drift) and a **phase retro** (after each command: summarize output, review all
  learnings, check every earlier artifact, propose updates with human confirmation,
  confirm readiness gate before proceeding).
- **FR-012**: `.agents/rules/base.md` MUST include a rule mandating that after every
  SpecKit phase the agent runs `/speckit.retro` before proceeding. This rule — not
  modifications to SpecKit's own command files — is the enforcement mechanism, ensuring
  the behavior survives SpecKit updates and is portable to new projects.
- **FR-013**: The rule in `base.md` MUST specify both retro modes: micro-retro after
  each implementation task (simplify + learn + iterate check + suggest `/clear`) and
  phase retro at every phase boundary (summarize + learning review + backwards artifact
  check + readiness gate + suggest `/clear`).
- **FR-014**: The AI agent MUST NOT silently update earlier SpecKit artifacts
  (`spec.md`, `plan.md`, `tasks.md`, `data-model.md`, `contracts/`) as a result of
  learnings discovered in a later phase. All proposed changes MUST be listed and
  confirmed by the human before being applied.
- **FR-015**: A `lessons-learned.md` file format MUST be documented so that all
  SpecKit phases write learnings in a consistent, scannable structure.
- **FR-016**: After every phase retro readiness gate passes, the agent MUST suggest
  running `/clear` before the next phase, stating exactly which files to re-read
  after the reset. This suggestion MUST be conditional — clearly framed as optional
  and most valuable for long sessions — never as a hard stop.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new AI agent session on a fresh clone can correctly describe the project
  architecture and run the correct test commands on the first attempt, without any human
  prompting.
- **SC-002**: 100% of PRs modifying code files receive an automated AI code review posted
  within 5 minutes of the PR being opened or updated.
- **SC-003**: Every PR modifying the agent rules file without an approval reference is
  blocked by CI with a clear, actionable error message pointing to the exact fix.
- **SC-004**: All common development operations (test, lint, docker, git status/diff/log)
  execute in Claude Code without triggering permission prompts.
- **SC-005**: A contributor new to the project can open a PR and, from the template alone,
  understand what validations are expected before requesting a review.
- **SC-006**: After every completed implementation task, the agent produces a micro-retro
  output (simplification notes or "nothing to simplify", plus learning log or "nothing
  unexpected") before starting the next task — with zero exceptions.
- **SC-007**: No SpecKit command transitions to the next phase without first producing an
  explicit "Ready / Blocked" readiness statement as its final output.
- **SC-008**: Any learning that contradicts an earlier artifact is surfaced to the human
  and documented in `lessons-learned.md` before the next phase begins — it is never
  silently discarded or silently applied.
- **SC-009**: After every phase retro readiness gate passes, the agent produces a
  session hygiene suggestion that names the specific files to re-read after a `/clear`,
  so no context is lost across the reset.
