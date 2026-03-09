# Lessons Learned: Agentic Development Infrastructure

**Feature**: `001-agentic-tooling`
**Started**: 2026-03-08

## implement phase — Task state hygiene not enforced by SpecKit

**What happened**: At the end of the implement phase, several tasks still showed as unchecked `[ ]` in `tasks.md` despite being complete, and `spec.md` retained `Status: Draft` instead of `Status: Implemented`.
**Impact**: Spec — stale status fields in `spec.md` and `tasks.md` create false signals for future sessions (agent reads "Draft" and assumes work is pending).
**Proposed action**: Add a closing checklist item to the implement retro: verify all completed tasks are marked `[x]` and `spec.md` status is updated to `Implemented` before the phase retro runs.
**Status**: Resolved

**Update (2026-03-09)**: Resolved — `spec.md` updated to `Status: Implemented` and all tasks marked `[x]` before commit.

## implement phase — .idea/ IDE directory not in .gitignore

**What happened**: IntelliJ `.idea/` directory was created locally and appeared as untracked in `git status`, requiring manual addition to `.gitignore` before the commit.
**Impact**: None — caught before committing.
**Proposed action**: Add `.idea/` to `.gitignore` as part of initial repo setup (already done in this PR).
**Status**: Resolved
