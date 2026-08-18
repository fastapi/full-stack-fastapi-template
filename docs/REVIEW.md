# How to Review This Submission

This repository is **not a GitHub fork** of the base template. It was cloned locally, implemented, and pushed as a standalone repo. There is therefore **no automatic GitHub PR or fork diff UI** against upstream.

Use one of the methods below instead.

## Base reference

| Item | Value |
|------|-------|
| Upstream template | [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) |
| Pristine baseline in this repo | commit `3f52abe` (`Init commit` — unmodified template snapshot) |
| All RBAC work | commits after `3f52abe` through `HEAD` |

## Option 1 — Diff inside this repo (fastest)

After cloning:

```bash
git clone <this-repository-url>
cd <project-directory>

# Full RBAC diff vs pristine template snapshot
git diff 3f52abe..HEAD

# Summary only
git diff --stat 3f52abe..HEAD

# Commit-by-commit review (recommended)
git log --oneline 3f52abe..HEAD
git show <commit>
```

## Option 2 — Compare to upstream template locally

```bash
git clone https://github.com/fastapi/full-stack-fastapi-template /tmp/fastapi-template
git clone <this-repository-url> /tmp/rbac-submission
cd /tmp/rbac-submission

git diff /tmp/fastapi-template/master..HEAD --stat
git diff /tmp/fastapi-template/master..HEAD
```

Pin a specific upstream tag if you prefer reproducibility, e.g. `git checkout <tag>` in the template clone before diffing.

## Option 3 — GitHub cross-repo compare (manual URL)

Replace `OWNER`, `REPO`, and branch if needed:

```
https://github.com/fastapi/full-stack-fastapi-template/compare/master...OWNER:REPO:main
```

Example shape (adjust to your clone URL):

```
https://github.com/fastapi/full-stack-fastapi-template/compare/master...yanhub:evios:main
```

GitHub only shows this if both repositories are accessible to the viewer.

## Option 4 — Helper script

```bash
./scripts/review-diff.sh          # stat vs Init commit
./scripts/review-diff.sh --full   # full patch vs Init commit
```

## What changed (summary)

RBAC-focused edits (~53 files). Highlights:

| Area | Key paths |
|------|-----------|
| Permission model | `backend/app/core/permissions.py`, `backend/app/api/deps.py` |
| API routes | `backend/app/api/routes/users.py`, `backend/app/api/routes/metrics.py` |
| Data model | `backend/app/models.py`, migration `a1b2c3d4e5f6_add_user_role.py` |
| Frontend | `frontend/src/lib/permissions.ts`, `usePermissions`, `AccessDenied`, routes |
| Tests | `backend/tests/api/routes/test_authorization.py` |
| Docs | `README.md`, `NOTES.md`, `docs/adr/`, `docs/ai-conversations/` |

Incremental commit history (newest first):

```
docs: add RBAC ADRs, NOTES, and bonus submission docs
feat: log authorization denials and add coverage test
chore: add compose.override.example.yml and gitignore local override
docs: add English AI conversation exports for submission
…
feat: add RBAC roles, permissions module, migration, and seed users
fix: adapt docker compose for local Docker Compose v2.16
```

## AI conversation copies

English exports: [docs/ai-conversations/](ai-conversations/)

## Related repository (Task 2)

Infrastructure task (Ghost on Hetzner) is a **separate greenfield repo** — see its `REVIEW.md` there.
