---
title: "CI/CD Pipeline"
doc-type: reference
status: published
last-updated: 2026-02-28
updated-by: "infra docs writer"
related-code:
  - .github/workflows/test-backend.yml
  - .github/workflows/playwright.yml
  - .github/workflows/pre-commit.yml
  - .github/workflows/deploy-staging.yml
  - .github/workflows/deploy-production.yml
  - .github/workflows/detect-conflicts.yml
  - .github/workflows/issue-manager.yml
  - .github/workflows/labeler.yml
  - .github/workflows/latest-changes.yml
  - .github/workflows/smokeshow.yml
  - .github/workflows/add-to-project.yml
  - scripts/test.sh
  - scripts/generate-client.sh
related-docs:
  - docs/deployment/environments.md
  - docs/getting-started/development.md
  - docs/testing/strategy.md
tags: [ci-cd, pipeline, deployment, automation, github-actions]
---

# CI/CD Pipeline

## Pipeline Overview

This project uses GitHub Actions for all CI/CD automation. Eleven workflows cover testing, code quality, deployment, and repository management.

```
Push / PR
   │
   ├── pre-commit.yml      ─ Lint, format, type check, generate client
   ├── test-backend.yml    ─ Pytest (59 tests), coverage >=90%
   ├── playwright.yml      ─ 61 E2E tests across 4 shards
   │
   └── On merge to main:
         ├── deploy-staging.yml   ─ Auto-deploy to staging (self-hosted runner)
         ├── latest-changes.yml   ─ Update release-notes.md
         └── smokeshow.yml        ─ Publish coverage HTML report

On GitHub Release (published):
   └── deploy-production.yml ─ Deploy to production (self-hosted runner)
```

---

## Workflow Inventory

| Workflow | File | Trigger(s) | Purpose | Runner |
|----------|------|------------|---------|--------|
| Test Backend | `test-backend.yml` | push main, PR (opened/sync) | Run Pytest + coverage | ubuntu-latest |
| Playwright Tests | `playwright.yml` | push main, PR (opened/sync), workflow_dispatch | E2E tests (4-shard matrix) | ubuntu-latest |
| pre-commit | `pre-commit.yml` | PR (opened/sync) | Lint, format, type check, client gen | ubuntu-latest |
| Deploy to Staging | `deploy-staging.yml` | push main | Build + deploy to staging | self-hosted (staging) |
| Deploy to Production | `deploy-production.yml` | release published | Build + deploy to production | self-hosted (production) |
| Conflict Detector | `detect-conflicts.yml` | push, pull_request_target (sync) | Label PRs with merge conflicts | ubuntu-latest |
| Issue Manager | `issue-manager.yml` | schedule (daily), issue events, PR labels, workflow_dispatch | Auto-close stale issues/PRs | ubuntu-latest |
| Labels | `labeler.yml` | pull_request_target (opened/sync/reopened/labeled/unlabeled) | Auto-label PRs; enforce required labels | ubuntu-latest |
| Latest Changes | `latest-changes.yml` | pull_request_target main (closed), workflow_dispatch | Append merged PR to release-notes.md | ubuntu-latest |
| Smokeshow | `smokeshow.yml` | workflow_run: Test Backend (completed) | Publish coverage HTML as GitHub status | ubuntu-latest |
| Add to Project | `add-to-project.yml` | pull_request_target, issues (opened/reopened) | Add PRs/issues to GitHub Project board | ubuntu-latest |

---

## Workflow: Test Backend

**File:** `.github/workflows/test-backend.yml`

### Triggers

| Event | Branches | Conditions |
|-------|----------|------------|
| `push` | main | All files |
| `pull_request` | Any | opened, synchronize |

### Jobs

| Job | Runner | Depends On |
|-----|--------|------------|
| `test-backend` | ubuntu-latest | — |

### Steps

1. Checkout code (`actions/checkout@v6`)
2. Set up Python 3.10 (`actions/setup-python@v6`)
3. Install uv (`astral-sh/setup-uv@v7`)
4. `docker compose down -v --remove-orphans` — clean slate
5. `docker compose up -d db mailcatcher` — start dependencies only
6. Run DB migrations: `uv run bash scripts/prestart.sh` (working-dir: `backend/`)
7. Run tests: `uv run bash scripts/tests-start.sh "Coverage for ${{ github.sha }}"` (working-dir: `backend/`)
   - Tests are located in `backend/tests/unit/` and `backend/tests/integration/`
   - Legacy test directories (`backend/tests/api/`, `backend/tests/crud/`) fail collection and are pending cleanup (AYG-72)
8. `docker compose down -v --remove-orphans` — cleanup
9. Upload `backend/htmlcov` as artifact `coverage-html` (hidden files included)
10. Enforce coverage: `uv run coverage report --fail-under=90`

### Artifacts

| Artifact | Produced By | Retention |
|----------|-------------|-----------|
| `coverage-html` | `test-backend` job | Default (90 days) |

### Secrets & Variables

None required beyond `GITHUB_TOKEN` (implicit).

---

## Workflow: Playwright Tests

**File:** `.github/workflows/playwright.yml`

### Triggers

| Event | Branches | Conditions |
|-------|----------|------------|
| `push` | main | All files |
| `pull_request` | Any | opened, synchronize |
| `workflow_dispatch` | Any | `debug_enabled` input (optional) |

Path filter (`dorny/paths-filter@v3`) — the `test-playwright` job only runs if these paths changed:
- `backend/**`
- `frontend/**`
- `.env`
- `compose*.yml`
- `.github/workflows/playwright.yml`

### Jobs

| Job | Runner | Depends On | Notes |
|-----|--------|------------|-------|
| `changes` | ubuntu-latest | — | Runs paths-filter; outputs `changed` flag |
| `test-playwright` | ubuntu-latest | `changes` | Matrix: 4 shards, `fail-fast: false`, 60 min timeout |
| `merge-playwright-reports` | ubuntu-latest | `test-playwright`, `changes` | Runs even if shards failed |
| `alls-green-playwright` | ubuntu-latest | `test-playwright` | Branch protection gate; allows skip |

### Steps — test-playwright (per shard)

1. Checkout (`actions/checkout@v6`)
2. Setup Bun (`oven-sh/setup-bun@v2`)
3. Setup Python 3.10 (`actions/setup-python@v6`)
4. Optional tmate debug session (if `workflow_dispatch` with `debug_enabled=true`)
5. Install uv (`astral-sh/setup-uv@v7`)
6. `uv sync` (backend)
7. `bun ci` (frontend)
8. `bash scripts/generate-client.sh` — regenerate TypeScript client
9. `docker compose build`
10. `docker compose down -v --remove-orphans`
11. Run tests: `docker compose run --rm playwright bunx playwright test --fail-on-flaky-tests --trace=retain-on-failure --shard=N/4`
12. `docker compose down -v --remove-orphans`
13. Upload blob report artifact `blob-report-N` (retention: 1 day)

### Steps — merge-playwright-reports

1. Checkout, setup Bun, `bun ci`
2. Download all `blob-report-*` artifacts
3. `bunx playwright merge-reports --reporter html ./all-blob-reports`
4. Upload merged HTML report as `html-report--attempt-N` (retention: 30 days)

### Artifacts

| Artifact | Produced By | Retention |
|----------|-------------|-----------|
| `blob-report-1` to `blob-report-4` | `test-playwright` (each shard) | 1 day |
| `html-report--attempt-N` | `merge-playwright-reports` | 30 days |

### Secrets

None required (uses `GITHUB_TOKEN` implicitly).

---

## Workflow: pre-commit

**File:** `.github/workflows/pre-commit.yml`

### Triggers

| Event | Branches | Conditions |
|-------|----------|------------|
| `pull_request` | Any | opened, synchronize |

### Jobs

| Job | Runner | Depends On |
|-----|--------|------------|
| `pre-commit` | ubuntu-latest | — |
| `pre-commit-alls-green` | ubuntu-latest | `pre-commit` (branch protection gate) |

### Steps

Checks `PRE_COMMIT` secret availability to differentiate own-repo vs fork:

**Own-repo (has secrets):**
1. Checkout PR branch head (full history, with `PRE_COMMIT` token)
2. Setup Bun, Python 3.11, uv (with cache)
3. `uv sync --all-packages`
4. `bun ci`
5. `uvx prek run --from-ref origin/${GITHUB_BASE_REF} --to-ref HEAD --show-diff-on-failure` (continue-on-error)
6. Commit and push auto-fixes if any (as `github-actions[bot]`)
7. Exit 1 if prek found errors

**Fork (no secrets):**
1. Default checkout
2. Same setup steps
3. Same prek run
4. `pre-commit-ci/lite-action@v1.1.0` handles commit/push for forks

### Pre-commit Hooks Run

- `check-added-large-files`
- `check-toml`
- `check-yaml --unsafe`
- `end-of-file-fixer` (excludes generated client and email templates)
- `trailing-whitespace` (excludes generated client)
- `biome check --write` (frontend files)
- `ruff check --fix` (Python files)
- `ruff format` (Python files)
- `mypy backend/app` (Python, strict mode)
- `bash scripts/generate-client.sh` (on backend changes)

### Secrets

| Name | Purpose | Required |
|------|---------|----------|
| `PRE_COMMIT` | Push auto-fixed code back to branch (own-repo only) | No (falls back to fork mode) |

---

## Workflow: Deploy to Staging

**File:** `.github/workflows/deploy-staging.yml`

### Triggers

| Event | Branches | Conditions |
|-------|----------|------------|
| `push` | main | All files |

**Note:** Skipped when `github.repository_owner == 'fastapi'` (template repository guard).

### Jobs

| Job | Runner | Depends On |
|-----|--------|------------|
| `deploy` | self-hosted (staging label) | — |

### Steps

1. Checkout (`actions/checkout@v6`)
2. `docker compose -f compose.yml --project-name $STACK_NAME_STAGING build`
3. `docker compose -f compose.yml --project-name $STACK_NAME_STAGING up -d`

### Environment Variables (from Secrets)

| Variable | Secret Source |
|----------|---------------|
| `ENVIRONMENT` | Hardcoded: `staging` |
| `DOMAIN` | `secrets.DOMAIN_STAGING` |
| `STACK_NAME` | `secrets.STACK_NAME_STAGING` |
| `SECRET_KEY` | `secrets.SECRET_KEY` |
| `FIRST_SUPERUSER` | `secrets.FIRST_SUPERUSER` |
| `FIRST_SUPERUSER_PASSWORD` | `secrets.FIRST_SUPERUSER_PASSWORD` |
| `SMTP_HOST` | `secrets.SMTP_HOST` |
| `SMTP_USER` | `secrets.SMTP_USER` |
| `SMTP_PASSWORD` | `secrets.SMTP_PASSWORD` |
| `EMAILS_FROM_EMAIL` | `secrets.EMAILS_FROM_EMAIL` |
| `POSTGRES_PASSWORD` | `secrets.POSTGRES_PASSWORD` |
| `SENTRY_DSN` | `secrets.SENTRY_DSN` |

---

## Workflow: Deploy to Production

**File:** `.github/workflows/deploy-production.yml`

### Triggers

| Event | Conditions |
|-------|------------|
| `release` published | Triggered by publishing a GitHub Release |

**Note:** Skipped when `github.repository_owner == 'fastapi'` (template repository guard).

### Jobs

| Job | Runner | Depends On |
|-----|--------|------------|
| `deploy` | self-hosted (production label) | — |

### Steps

1. Checkout (`actions/checkout@v6`)
2. `docker compose -f compose.yml --project-name $STACK_NAME_PRODUCTION build`
3. `docker compose -f compose.yml --project-name $STACK_NAME_PRODUCTION up -d`

### Environment Variables (from Secrets)

| Variable | Secret Source |
|----------|---------------|
| `ENVIRONMENT` | Hardcoded: `production` |
| `DOMAIN` | `secrets.DOMAIN_PRODUCTION` |
| `STACK_NAME` | `secrets.STACK_NAME_PRODUCTION` |
| `SECRET_KEY` | `secrets.SECRET_KEY` |
| `FIRST_SUPERUSER` | `secrets.FIRST_SUPERUSER` |
| `FIRST_SUPERUSER_PASSWORD` | `secrets.FIRST_SUPERUSER_PASSWORD` |
| `SMTP_HOST` | `secrets.SMTP_HOST` |
| `SMTP_USER` | `secrets.SMTP_USER` |
| `SMTP_PASSWORD` | `secrets.SMTP_PASSWORD` |
| `EMAILS_FROM_EMAIL` | `secrets.EMAILS_FROM_EMAIL` |
| `POSTGRES_PASSWORD` | `secrets.POSTGRES_PASSWORD` |
| `SENTRY_DSN` | `secrets.SENTRY_DSN` |

---

## Workflow: Conflict Detector

**File:** `.github/workflows/detect-conflicts.yml`

### Triggers

| Event | Conditions |
|-------|------------|
| `push` | All branches |
| `pull_request_target` | synchronize |

### Jobs

| Job | Runner | Steps |
|-----|--------|-------|
| `main` | ubuntu-latest | `eps1lon/actions-label-merge-conflict@v3` — adds `conflicts` label and posts a comment if a PR has a merge conflict |

### Permissions

- `contents: read`
- `pull-requests: write`

---

## Workflow: Issue Manager

**File:** `.github/workflows/issue-manager.yml`

### Triggers

| Event | Schedule / Conditions |
|-------|-----------------------|
| `schedule` | Daily at 17:21 UTC |
| `issue_comment` | created |
| `issues` | labeled |
| `pull_request_target` | labeled |
| `workflow_dispatch` | Manual |

**Note:** Only runs when `github.repository_owner == 'fastapi'` — not active in forks or your own copy.

### Behavior

Uses `tiangolo/issue-manager@0.6.0` to auto-close items based on label:

| Label | Delay | Action |
|-------|-------|--------|
| `answered` | 10 days | Close with message |
| `waiting` | ~1 month | Close with message (3-day advance reminder) |
| `invalid` | Immediate | Close with message |
| `maybe-ai` | Immediate | Close with message (AI-generated content policy) |

---

## Workflow: Labels

**File:** `.github/workflows/labeler.yml`

### Triggers

| Event | Conditions |
|-------|------------|
| `pull_request_target` | opened, synchronize, reopened, labeled, unlabeled |

### Jobs

| Job | Runner | Depends On | Purpose |
|-----|--------|------------|---------|
| `labeler` | ubuntu-latest | — | `actions/labeler@v6` — auto-apply path-based labels |
| `check-labels` | ubuntu-latest | `labeler` | Enforce one of: `breaking`, `security`, `feature`, `bug`, `refactor`, `upgrade`, `docs`, `lang-all`, `internal` |

PRs missing a required label will fail the `check-labels` step.

---

## Workflow: Latest Changes

**File:** `.github/workflows/latest-changes.yml`

### Triggers

| Event | Branches | Conditions |
|-------|----------|------------|
| `pull_request_target` | main | closed (merged) |
| `workflow_dispatch` | Any | PR number input required |

### Jobs

| Job | Runner | Steps |
|-----|--------|-------|
| `latest-changes` | ubuntu-latest | Checkout (with `LATEST_CHANGES` token to push to main), then `tiangolo/latest-changes@0.4.1` — appends PR info to `release-notes.md` under `## Latest Changes` header |

### Secrets

| Name | Purpose |
|------|---------|
| `LATEST_CHANGES` | Personal access token with push permission to main for auto-committing release notes |
| `GITHUB_TOKEN` | Read PR data |

---

## Workflow: Smokeshow

**File:** `.github/workflows/smokeshow.yml`

### Triggers

| Event | Conditions |
|-------|------------|
| `workflow_run` | Triggered when `Test Backend` workflow completes |

### Jobs

| Job | Runner | Steps |
|-----|--------|-------|
| `smokeshow` | ubuntu-latest | Checkout, Python 3.13, `pip install smokeshow`, download `coverage-html` artifact from triggering run, `smokeshow upload backend/htmlcov` |

Sets a GitHub commit status `coverage` with the coverage percentage. Fails if coverage < 90%.

### Secrets

| Name | Purpose | Required |
|------|---------|----------|
| `SMOKESHOW_AUTH_KEY` | Smokeshow service auth key | Yes |
| `GITHUB_TOKEN` | Download artifacts, set commit status | Yes (auto) |

---

## Workflow: Add to Project

**File:** `.github/workflows/add-to-project.yml`

### Triggers

| Event | Conditions |
|-------|------------|
| `pull_request_target` | All activity |
| `issues` | opened, reopened |

### Jobs

| Job | Runner | Steps |
|-----|--------|-------|
| `add-to-project` | ubuntu-latest | `actions/add-to-project@v1.0.2` — adds item to GitHub Project board |

**Note:** The project URL is configured for the upstream `fastapi` org project. Update this for your own project board.

### Secrets

| Name | Purpose |
|------|---------|
| `PROJECTS_TOKEN` | Personal access token with `project` scope |

---

## Branch → Pipeline Mapping

| Event | Workflows Triggered | Deploy Target |
|-------|---------------------|---------------|
| PR opened or updated | pre-commit, Test Backend, Playwright (if paths changed) | None |
| Push to `main` | Test Backend, Playwright, Deploy Staging, Latest Changes | Staging |
| GitHub Release published | Deploy Production | Production |
| `workflow_run: Test Backend` completes | Smokeshow | — (coverage report) |
| PR opened/closed | Add to Project, Labels, Conflict Detector, Latest Changes | — |

---

## Required Secrets

Configure these in: **GitHub repository → Settings → Secrets and variables → Actions**

### Deployment Secrets (Required for staging/production)

| Secret | Used By | Description |
|--------|---------|-------------|
| `DOMAIN_STAGING` | `deploy-staging.yml` | Staging domain (e.g. `staging.example.com`) |
| `DOMAIN_PRODUCTION` | `deploy-production.yml` | Production domain (e.g. `example.com`) |
| `STACK_NAME_STAGING` | `deploy-staging.yml` | Docker Compose project name for staging |
| `STACK_NAME_PRODUCTION` | `deploy-production.yml` | Docker Compose project name for production |
| `SECRET_KEY` | Both deploy workflows | JWT signing key — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `FIRST_SUPERUSER` | Both deploy workflows | Admin email for initial superuser |
| `FIRST_SUPERUSER_PASSWORD` | Both deploy workflows | Admin password |
| `POSTGRES_PASSWORD` | Both deploy workflows | Database password |
| `SMTP_HOST` | Both deploy workflows | SMTP server hostname |
| `SMTP_USER` | Both deploy workflows | SMTP username |
| `SMTP_PASSWORD` | Both deploy workflows | SMTP password |
| `EMAILS_FROM_EMAIL` | Both deploy workflows | Sender email address |
| `SENTRY_DSN` | Both deploy workflows | Sentry DSN for error tracking (optional) |

### Automation Secrets (Optional)

| Secret | Used By | Description |
|--------|---------|-------------|
| `PRE_COMMIT` | `pre-commit.yml` | PAT with push permission — allows bot to commit auto-fixes |
| `LATEST_CHANGES` | `latest-changes.yml` | PAT with push permission — allows bot to commit release notes |
| `SMOKESHOW_AUTH_KEY` | `smokeshow.yml` | Smokeshow.io auth key for hosting coverage reports |
| `PROJECTS_TOKEN` | `add-to-project.yml` | PAT with `project` scope for GitHub Projects integration |

---

## Self-Hosted Runners

Staging and production deployments require self-hosted runners registered with specific labels:

| Label | Used By | Purpose |
|-------|---------|---------|
| `staging` | `deploy-staging.yml` | Runner on staging server with Docker access |
| `production` | `deploy-production.yml` | Runner on production server with Docker access |

The runner must have:
- Docker and Docker Compose installed
- Access to the deploy environment secrets via the workflow
- The project code at `/root/code/app/` (or adjust workflow accordingly)

To register a runner: **GitHub repository → Settings → Actions → Runners → New self-hosted runner**

---

## Local Reproduction

Run all CI checks locally before pushing:

```bash
# Backend: lint, type check, format
cd backend
uv run ruff check --fix
uv run ruff format
uv run mypy backend/app

# Backend: tests with coverage
# Target unit and integration tests (legacy test directories are pending cleanup)
uv run pytest backend/tests/unit/ backend/tests/integration/ -v --cov=app
uv run coverage report --fail-under=90

# Frontend: lint
cd frontend
bun run lint

# Frontend: E2E tests (requires full stack running)
docker compose watch  # In another terminal
bunx playwright test

# All pre-commit hooks
cd backend
uv run prek run --all-files

# Generate API client (after backend changes)
bash scripts/generate-client.sh
```

---

## Dependencies

### Backend Runtime Dependencies

The backend requires these core dependencies (defined in `backend/pyproject.toml`):

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `fastapi` | >=0.114.2 | Web framework |
| `sqlmodel` | >=0.0.21 | ORM with SQLAlchemy |
| `pydantic-settings` | >=2.2.1 | Configuration management |
| `sentry-sdk` | >=2.0.0 | Error tracking |
| `structlog` | >=24.1.0 | Structured logging |
| `supabase` | >=2.0.0 | Supabase client library |
| `clerk-backend-api` | >=1.0.0 | Clerk authentication |
| `pyjwt` | >=2.8.0 | JWT token handling |
| `pwdlib` | >=0.3.0 | Password hashing (Argon2, Bcrypt) |

**Test Environment Requirements:**

For CI/CD pipelines, ensure these environment variables are set:

```bash
SUPABASE_URL=<project-url>           # Required
SUPABASE_SERVICE_KEY=<service-key>   # Required, must be valid (not "changethis")
CLERK_SECRET_KEY=<secret-key>        # Required, must be valid (not "changethis")
ENVIRONMENT=local                    # Relaxed validation for tests
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Test Backend fails on migration step | DB not healthy yet | Check `docker compose up -d db mailcatcher` health check passes before prestart |
| Coverage below 90% | New code without tests | Add tests; view coverage report in Artifacts → `coverage-html` |
| Playwright shards fail inconsistently | Flaky tests (`--fail-on-flaky-tests`) | Identify flaky test from HTML report artifact; fix race conditions |
| Deploy to staging fails | Self-hosted runner offline | Check runner status in Settings → Actions → Runners |
| Deploy to production fails | Missing `DOMAIN_PRODUCTION` secret | Add all required deployment secrets to GitHub |
| pre-commit fails on fork | No `PRE_COMMIT` secret (expected) | Fork uses `pre-commit-ci/lite-action` fallback — this is normal |
| Labels check fails | PR missing required label | Add one of: `breaking`, `security`, `feature`, `bug`, `refactor`, `upgrade`, `docs`, `lang-all`, `internal` |
| Smokeshow fails | Missing `SMOKESHOW_AUTH_KEY` | Register at smokeshow.io and add key to secrets |
| Tests pass locally but fail in CI | Python or Bun version mismatch | CI uses Python 3.10 and Bun latest — check your local versions match |
