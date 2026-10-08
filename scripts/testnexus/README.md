# TestNexus full-stack setup

This branch runs the upstream backend suite, a live HTTP item lifecycle, and the
complete Chromium suite (including email password recovery). FastAPI serves the
built React frontend. PostgreSQL and Mailpit are disposable supporting services.
Only use isolated test data: backend fixtures delete application users and items.

## Operator preparation

Build from this repository root, on the Docker host used by the TestNexus worker:

```powershell
docker build -f scripts/testnexus/Dockerfile -t testnexus-fullstack:local .
docker image inspect testnexus-fullstack:local postgres:17 testnexus-runner:local
```

If PostgreSQL is missing, provision it with `docker pull postgres:17`. The normal
TestNexus bootstrap image `testnexus-runner:local` must also already be built.
Append `testnexus-fullstack:local` to both `RUNNER_IMAGES` and `SERVICE_IMAGES`
in the TestNexus backend environment. Preserve existing allowed images. Reload
the API and recreate the worker/dispatcher after active runs finish. No registry
push is needed when Docker Desktop and the worker use the same Docker daemon.

## System and environment

| Field | Value |
|---|---|
| System name | Full-stack FastAPI |
| Repository | https://github.com/Chantal-Marissa-Pande/full-stack-fastapi-template.git |
| Default branch | testnexus |
| Technology stack | Python 3.14, FastAPI, React, TypeScript, Bun, PostgreSQL, Playwright |
| Owner/team | Your QA team |
| Description | Disposable full-stack backend, system and browser verification |
| Environment name | Full-stack Development |
| Environment type | development |
| Target URL | Leave blank; the worker creates a private per-run URL |
| Environment description | Isolated application, database and test email service |

## Pipeline

| Field | Value |
|---|---|
| Runner preset | Browser, then override Runner image with the value below |
| Runner image | testnexus-fullstack:local |
| Pipeline name | Full-stack acceptance |
| Target environment | Full-stack Development |
| Repository branch | testnexus |
| Dependency installation | sh scripts/testnexus/install.sh |
| Minimum pass rate | 100 |
| Minimum line coverage | Leave blank initially |
| Description | Backend, live API/database workflow and Chromium acceptance tests |

## Deployment testing

| Field | Value |
|---|---|
| Application deployment | Isolated/per-run application |
| Startup command | python scripts/testnexus/run.py start |
| Application port | 8000 |
| Memory | 4096 MiB |
| Workspace | 6144 MiB |
| CPU cores | 2 |
| Process limit | 512 |
| Browser shared memory | 512 MiB |
| Temporary storage | 512 MiB |
| Run timeout | 1800 seconds |
| Readiness timeout | 120 seconds |
| Setup timeout | 120 seconds |
| After a stage fails | Continue, to collect evidence from all suites |
| Readiness path | /api/v1/utils/health-check/ |
| Test data setup | Leave blank; startup migrates/seeds and later stages reseed |
| Test data teardown | Leave blank; per-run services and database are removed |
| Diagnostic files | Leave blank initially; never collect browser authentication state |

Application variables (non-secret):

```text
PROJECT_NAME=TestNexus full-stack fixture
FIRST_SUPERUSER=admin@example.com
EMAILS_FROM_EMAIL=noreply@example.com
APP_DATABASE_USER=testnexus_fixture
APP_DATABASE_NAME=testnexus_fixture
CI=true
```

Application secret references (names only):

```text
TEST_DATABASE_PASSWORD=fullstack-db-password
FIRST_SUPERUSER_PASSWORD=fullstack-admin-password
SECRET_KEY=fullstack-signing-key
```

After registering the environment, an operator must provision those three values
under its organization/environment IDs in the worker secret provider. Generate
random test-only values. The database service must reference the **same**
`fullstack-db-password`. Never put actual values in this public repository or in
the pipeline form. The worker assembles the database URL in memory.

Supporting services:

| Field | Database | Email |
|---|---|---|
| Name | database | mail |
| Type | PostgreSQL | Process |
| Image | postgres:17 | testnexus-fullstack:local |
| Startup command | Leave blank (preset) | mailpit --listen 0.0.0.0:8025 --smtp 0.0.0.0:1025 |
| Port | 5432 | 8025 |
| Memory | 512 MiB | 256 MiB |
| Storage | 256 MiB | 256 MiB |
| Variables | POSTGRES_USER=testnexus_fixture; POSTGRES_DB=testnexus_fixture | Leave blank |
| Secret reference | POSTGRES_PASSWORD=fullstack-db-password | Leave blank |

Enter the database variables on separate lines. The email service listens on
SMTP 1025 as well as HTTP 8025; both are internal to the private run network.
No host ports, Docker socket, external database or public email service is needed.

## Ordered test stages

All stages use working directory `.` and are required. Commands generate their
JUnit report relative to that root. Set the backend Cobertura path to
`backend/test-results/coverage.xml`; leave the other coverage paths blank.

| Stage | Suite type | Framework | Command | Timeout | JUnit report |
|---|---|---|---|---|---|
| Backend | integration | pytest | python scripts/testnexus/run.py backend | 600 | backend/test-results/backend.xml |
| Live system workflow | system | pytest | python scripts/testnexus/run.py system | 180 | test-results/system.xml |
| Chromium acceptance | e2e | Playwright | python scripts/testnexus/run.py browser | 1200 | frontend/test-results/browser.xml |

The backend stage includes upstream unit/API/database tests. The system stage
uses real HTTP requests to check frontend availability, login, item creation,
database retrieval and deletion. Chromium covers the upstream browser journeys,
including password reset through Mailpit. Backend teardown deletes the seeded
account, so subsequent stages restore it before authentication.

The overall 1800-second run timeout also includes checkout, installation and
startup; stage timeouts are ceilings, not reserved time. Slow first downloads may
require retrying after caches/image provisioning finish. A gate passes only when
required reports are valid and every suite meets its configured threshold.

## Verified baseline

Verified on Docker Desktop on 2026-10-08 using non-root containers, read-only root
filesystems, a shared bounded workspace, and an internal network. Locked
dependency installation and the frontend build passed. Results were 58 backend
tests, 1 live system workflow and 62 Chromium tests passed; backend line coverage
was 91.23%. JUnit reports and the backend Cobertura report were generated. The
disposable verification database, services, application, network and workspace
were removed afterwards. These results are a local baseline; register the new
TestNexus environment and provision its scoped secrets before submitting a run.
