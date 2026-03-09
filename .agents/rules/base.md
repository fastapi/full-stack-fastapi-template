# Base Agent Rules

> Single source of truth for AI agent conventions in this project. Read this file at the start of every session before doing anything else.

## Project Overview

This is a full-stack web application with a Python backend and TypeScript/Node 22 frontend.

**Backend**: Python 3.10+, FastAPI, SQLModel, PostgreSQL, managed with `uv`
**Frontend**: TypeScript, Node 22, ESM-only, managed with `bun`
**CI/CD**: GitHub Actions — automated tests, linting, Docker compose validation, Claude AI review
**Infrastructure**: Docker Compose for local development and CI

Architecture: HTTP API (backend) consumed by a single-page frontend. Services run in Docker containers locally and in staging/production via GitHub Actions deployments.

```
full-stack-agentic/
  backend/          Python FastAPI application
  frontend/         TypeScript/Node 22 frontend
  .github/          CI workflows, PR templates, CODEOWNERS
  .agents/rules/    AI agent conventions (this directory)
  .claude/          Claude Code settings and commands
  specs/            Feature specifications (SpecKit artifacts)
```

## Project Structure

```
.
├── backend/
│   ├── app/            Application source (routers, models, services)
│   ├── tests/          pytest test suite
│   └── pyproject.toml
├── frontend/
│   ├── src/            TypeScript source
│   └── package.json
├── .github/
│   ├── workflows/      CI workflow files
│   ├── CODEOWNERS      Auto-review assignments
│   └── pull_request_template.md
├── .agents/
│   └── rules/          Agent rule files (base.md, coding-standards.md, ai-feedback-learning-loop.md)
├── .claude/
│   ├── commands/       SpecKit skill files
│   └── settings.json   Shared Claude tool permissions
└── specs/              Per-feature SpecKit artifacts
```

## Available Commands

### Backend Tests

```bash
uv run pytest
```

```bash
uv run python -m pytest
```

### Backend Lint

```bash
uv run ruff check .
```

```bash
uv run ruff format .
```

### Backend Type Check

```bash
uv run ty check
```

### Frontend Tests

```bash
bun run test
```

### Frontend Lint

```bash
bun run lint
```

### Docker (local dev)

```bash
docker compose up
```

```bash
docker compose down
```

### SpecKit Scripts

```bash
.specify/scripts/bash/<script-name>
```

## Testing Conventions

- Backend tests live in `backend/tests/`, mirroring the `app/` package structure
- Run with `uv run pytest` from the repo root or `backend/` directory
- Frontend tests are colocated (`*.test.ts`) alongside source files
- Run with `bun run test` from `frontend/`
- Test behavior, not implementation — tests verify what code does, not how
- Mock only boundaries: network, filesystem, external services
- Every error path the code handles should have a test

## SpecKit Workflow

This project uses SpecKit for structured feature development. The phases are:
`/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`

Artifacts live in `specs/<feature-id>-<feature-name>/`.

### Retro Gate (mandatory)

After every SpecKit phase command completes (`/speckit.specify`, `/speckit.plan`,
`/speckit.tasks`, `/speckit.implement`), run `/speckit.retro` before starting
the next phase. Do not proceed until the retro produces a "Ready" status.

**Micro-retro** (after each task in `/speckit.implement`):
1. Simplify the code just written
2. Log anything unexpected to `specs/<feature>/lessons-learned.md`
3. Check whether `tasks.md`, `plan.md`, or `spec.md` needs updating
4. Suggest `/clear` before the next task

**Phase retro** (after each phase command):
1. Summarize what was produced
2. Review `lessons-learned.md`
3. Check all earlier artifacts for drift
4. Propose constitution/rules updates (never self-apply — await human approval)
5. Confirm readiness gate (5 items)
6. Suggest `/clear` with specific files to re-read

## Rule Proposal Process

When you receive a correction or discover a pattern worth preserving project-wide, propose a rule change following the process in `.agents/rules/ai-feedback-learning-loop.md`.

Key constraint: **never self-apply rule changes**. Always propose and wait for explicit human approval before modifying any file in `.agents/rules/`.

## SDD Development Workflow

1. **Branch**: Create a feature branch from `master` — `git checkout -b <id>-<short-name>`
2. **Develop**: Implement the feature; run tests and linter locally before committing
3. **PR**: Open a pull request against `master` using the PR template in `.github/pull_request_template.md`
4. **CI**: GitHub Actions runs tests, lint, and automated Claude code review
5. **Review**: CODEOWNERS auto-requests designated reviewers for affected paths
6. **Merge**: Merge after CI passes and reviewers approve — no direct pushes to `master`

Changes to `.agents/rules/base.md` require a `Rule-Change-Approval: <ref>` line in the PR description. CI will block the PR if absent.
