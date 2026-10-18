# Independent repo reading and FDE training

## Purpose

Use this repo to build the ability to understand unfamiliar systems, debug from evidence, ship small changes, and explain decisions to a customer or teammate. FDE means forward deployed engineer here: practice turning an unclear user problem into a working, verifiable solution.

This file is the persistent training record. Read it at the start of every training conversation; do not rely on chat memory.

## How to ask for today's task

Paste this into a new conversation:

> Read TRAINING.md and give me today's task. Check my latest evidence and select the next unfinished session. Give me one bounded assignment with a scenario, time budget, deliverables, and completion criteria. Do not solve it, explain the code in advance, or edit implementation files. Help me learn to navigate independently. If I get stuck, start with a question or a small hint. After I submit my work, review it against the code and update TRAINING.md with my permission to record progress.

To submit work:

> Review my session evidence against TRAINING.md and the repo. Here are my notes, commands, results, and any diff: [...]. Record what I demonstrated, what needs correction, and the next session. Do not implement corrections for me.

## Coaching rules

- Give one small assignment at a time, currently 20-30 minutes and one new skill. A numbered session can span several days; do not advance just because a day passed. Larger sessions below are milestones, not daily workloads.
- Start with the next unfinished session unless submitted evidence shows a prerequisite needs practice. Recheck paths against the current checkout.
- Let me try independently for 10-15 minutes before offering help; I can request help sooner. I may use repository docs, official documentation, search, the debugger, and existing tests. AI should not generate my solution or summarize the relevant code before I try.
- Ask me to predict behavior before running an experiment. Separate predictions, observations, and explanations.
- Use a hint ladder only when requested: guiding question, useful search term or file, relevant symbol, then a small explanation. Give a full walkthrough only if I explicitly request one; record that the skill needs an independent retry.
- Require evidence: paths and symbols, commands and observed output, a diagram or explanation in my own words, and tests when behavior changes. Never record an unrun check as passed.
- Review reasoning as well as correctness. Ask a follow-up that changes one assumption to check whether I understand.
- For implementation tasks, have me make the change, choose a focused check, inspect the diff, and write a short reviewable explanation. Keep experiments local and use disposable test data; never include credentials or tokens in notes.
- Prefer a small follow-up over adding several new concepts when a session is incomplete. Documentation-only sessions do not require code changes.
- Current calibration: the learner follows explanations of endpoint selection and dependencies, but independent navigation is not yet demonstrated. Practice finding an entry point, following an import, and explaining a connection before combining these with token internals, database lifecycle, and test fixtures. Explain one step at a time when asked, and pause for the learner's response.
- Increase scope after two small assignments completed independently with code references and a correct explanation. Understanding a walkthrough is progress but is not evidence of independent mastery. If stuck, reduce the number of concepts and offer one hint rather than supplying the whole trace.

## Progress

| Session | Status | Evidence / remaining uncertainty |
| --- | --- | --- |
| S1: Run the stack and fix a real bug | Done, reported by learner | Full stack running. Found Windows decoding failure in `backend/app/utils.py`: `render_email_template` used `read_text()` without explicit encoding. Fixed with `encoding="utf-8"`. Local commit `f8e6991` on `fix-email-template-encoding`. Local remote-tracking ref `origin/fix-email-template-encoding` matches that commit at setup; live remote and PR open/merged status have not been verified. |
| S2: Map the backend | Done, reported by learner | Mapped `backend/app/main.py`, `api/main.py`, `api/deps.py`, `core/config.py`, `models.py`, and `crud.py`. Existing `NOTES.md` says the current reading location is `backend/app/api/deps.py`. |
| S3: Trace one authenticated request | In progress; follow-up tomorrow | Reviewed `NOTES.md`: correctly identified login/token issuance and ownership filtering, but traced the item list instead of the single-item endpoint and attributed its restriction to an unrelated superuser dependency. No execution evidence submitted yet. |

Next assignment: **S3a, scheduled for 2026-10-19**. Complete only the small assignment below. No further work is expected on the day of this review.

## S3a: Find the handler and follow one dependency (20-30 minutes)

Today's review supplied an explanation of the request path. Tomorrow, reconstruct it independently rather than copying that explanation. No implementation change required.

1. Starting from "open one item," search the backend and find the handler. Record the search you used and explain which decorator and function name distinguish it from the list endpoint.
2. Read the handler's signature. Identify which parameter comes from the URL and which parameter represents the current user.
3. Follow the current-user parameter's type through its import to its definition. Write a short chain ending at the function that supplies the user. Stop there: token internals, database cleanup, and tests belong to later assignments.

**Deliverable:** Short answers in your own words in `NOTES.md`, `training/S3.md`, or chat. Reference paths and symbols instead of copying large code blocks.

**Complete when:** You can reconstruct the search and dependency chain from the code, explain each connection, and distinguish separate endpoints from functions invoked as dependencies. It is fine to consult the source; do not copy the earlier walkthrough as your answer.

**Review question:** What code proves which function supplies the current user?

### Later S3 assignments: give only one after reviewing the previous one

- **S3b: Read decisions.** Follow `read_item` in order. Predict missing-item, wrong-owner, own-item, and superuser outcomes with deciding conditions. Explain whether the ownership check executes when the item is missing.
- **S3c: Follow authentication.** Trace how the token becomes a user. Separate token extraction, validation, user lookup, and active-user checks. Assemble the full request URL from router prefixes.
- **S3d: Follow the session.** Trace `SessionDep` to its provider and explain `yield` and session cleanup. Keep this separate from learning test fixtures.
- **S3e: Observe behavior.** Start with one existing single-item test: explain setup, request, and assertion, then run it or reproduce the request. Expand to three observed cases across further small assignments as needed. Record commands and actual results; mark unrun checks explicitly.

**After these reviews:** Assemble the original S3 deliverables below from accumulated notes. Do not assign the entire original task again. Completing S3a alone does not complete S3.

## S3: Why can this user see this item?

**Scenario:** A customer says, "I can log in, but opening an item sometimes fails. Where does the application decide whether I can see it?"

**Budget:** 60 minutes. Investigate and explain; no implementation change required.

1. Spend 5 minutes sketching your prediction of the path from an HTTP request to the item response, using what you remember from S2.
2. Find the single-item GET endpoint. Trace how its URL is assembled, how its dependencies execute, how a token becomes a user, how the database session is supplied, and where access to the item is decided. Follow symbols only as needed; avoid reading every file.
3. Make a prediction table for: no token, malformed token, valid token belonging to an inactive user, nonexistent item, another user's item, your own item, and a superuser opening another user's item. For each, predict the status and identify the deciding symbol. Use valid item UUIDs and state other assumptions so each case isolates one cause.
4. Inspect the existing route tests and fixtures. Run or reproduce at least three cases locally, including one failure. Record the exact command or request with secrets removed, the observed status, and any mismatch with your prediction. Identify which other cases existing tests cover and which remain unverified.
5. Close the source and give a two-minute explanation in your own words. Then reopen it to check your explanation.

**Deliverables:** A request-flow sketch, the prediction/observation table, references to relevant paths and symbols, and a short customer-facing explanation of what you would investigate next. Save notes in `training/S3.md` when you do the session, or submit them in chat.

**Complete when:** You can distinguish authentication from item authorization; explain dependency resolution and session cleanup; locate each decision in code; and support at least three cases with observations. Unsupported guesses or a copied code summary require a follow-up.

**Stretch, only if time remains:** Explain what changes if the token is valid but its user no longer exists. Predict before checking.

## Progression after S3

These are a sequence of candidate sessions, not a set of simultaneous assignments. The coach should turn the next row into a concrete task based on my latest evidence. Increase scope gradually and revisit weak areas.

| Session | Skill and scenario | Evidence to produce |
| --- | --- | --- |
| S4 | Follow an item creation from request validation to persistence and response. | Trace input/table/output models; explain commit and refresh; predict invalid input and confirm one case. |
| S5 | Trace a browser action across the frontend and backend. | Follow `frontend/src/components/Items/AddItem.tsx` through the generated client to the route; show the browser request and how success/error reaches the UI. |
| S6 | Investigate a login or password-reset support ticket. | Reproduction, ranked hypotheses, token/email flow, and a concise customer update with no exposed secrets. |
| S7 | Understand test isolation and add one useful missing regression check. | Explain fixtures in `backend/tests/conftest.py`; demonstrate the check detects the intended failure and passes after correction. |
| S8 | Deliver a small customer-requested change. | Clarify acceptance criteria, identify affected layers, implement a bounded change, run focused checks, and write a PR description. Choose scope after S7. |
| S9 | Change persistent data safely. | Explain existing Alembic history; propose a small schema change, inspect generated SQL, and practice migration on a disposable local database. Document rollback limits. |
| S10 | Diagnose a startup or configuration failure. | Trace settings, database startup, and Compose service dependencies; collect logs and test one hypothesis at a time. |
| S11 | Explain how a change reaches users. | Trace relevant GitHub Actions and deployment docs; identify build/test gates, configuration, failure signals, and a recovery plan. No live deployment needed. |
| S12 | Practice discovery with an ambiguous customer request. | Write clarifying questions, user outcome, constraints, acceptance criteria, and two options with tradeoffs; select a small vertical slice. |
| S13 | Build the agreed vertical slice independently. | Working local demo, focused validation, documented limitations, and a short handoff another engineer can use. |
| S14 | Rehearse an incident and handoff. | Timeline of evidence, root cause versus symptoms, recovery verification, prevention proposal, and a five-minute explanation. |
| S15 | Transfer the method to unfamiliar code. | Pick a previously unread subsystem or another repo; find its entry points, trace one behavior, and explain it with evidence within 60 minutes. |

Useful anchors: `development.md`, `backend/README.md`, `frontend/README.md`, `backend/tests/`, `backend/app/alembic/`, `scripts/generate-client.sh`, `.github/workflows/`, `deployment.md`, and `deployment-docker-compose.md`. These are starting points, not substitutes for tracing actual behavior.

## Session record template

Append one record after each reviewed attempt. Keep detailed evidence in `training/S<number>.md` if useful; keep the progress table and next-session pointer current.

```markdown
### S__ - Title - YYYY-MM-DD
- Status: in progress / needs follow-up / complete
- Time spent:
- Scenario and acceptance criteria:
- Initial prediction:
- Paths and symbols followed:
- Commands/requests and observed results (redacted):
- What I can now explain without the source open:
- Incorrect assumptions and corrections:
- AI hints used:
- Validation run / not run:
- Review: navigation / mental model / evidence / communication
- Remaining gap and next session:
```

Use the review fields as a simple rubric: **independent**, **with hints**, or **needs retry**. Completion means the session criteria are met and I can answer a changed-assumption question; it does not mean every skill is mastered. Revisit areas marked "with hints" in a later independent task.
