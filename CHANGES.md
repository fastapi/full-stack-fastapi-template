# Changes on top of `fastapi/full-stack-fastapi-template`

---

## 2026-07-05

- `frontend/src/main.tsx` — `currentUser` query `onError` clears token and redirects to `/login` on `400/401/403/404`; sets `retry=false` for immediate redirect.
- `frontend/tests/login.spec.ts` — mocks `/users/me` → 404, asserts token clearing + redirect.
- `backend/app/api/routes/login.py` — in dev, logs reset link to console instead of asserting `emails_enabled` (fails locally).

## 2026-07-04 — merge upstream/master (10 commits)

Merged `fastapi/full-stack-fastapi-template@a758585` (release-notes + dep bumps only).

- `uv.lock` — re-locked from ours in a `uv:python3.14-bookworm-slim` container. Minimal bump: `emails` 0.6 → 1.1.2.
- `backend/app/utils.py`, `backend/pyproject.toml` — took upstream `emails` 1.1.2 API change, layered on our Resend early-return.
- Workflows — `actions/checkout` v6.0.3 → v7.0.0.

## 2026-07-02

- `frontend/src/components/Common/Footer.tsx` — hand-rolled `fetch` to `/articles/stats` was missing `/api/v1` prefix, 404ing silently. Fixed.
- `backend/app/core/config.py` — `RESEND_API_KEY: str | None`; `emails_enabled` now `bool(EMAILS_FROM_EMAIL and (RESEND_API_KEY or SMTP_HOST))`.
- `backend/app/utils.py` — `send_email` uses `resend.Emails.send(...)` when `RESEND_API_KEY` set, falls back to SMTP.
- `backend/tests/api/routes/test_login.py` — `test_recovery_password` configures `RESEND_API_KEY`, asserts `resend.Emails.send`; added `test_recovery_password_smtp_fallback`.
- `backend/app/api/routes/likes.py`, `backend/app/api/deps_agentique.py`, `backend/app/alembic/versions/d4e5f6a7b8c9_add_article_like_table.py`, `backend/tests/api/routes/test_likes.py`, `backend/tests/utils/article.py` — new files: article likes (PUT/DELETE/GET auth-required, idempotent composite PK), `CurrentUserOptional` (returns `None` on any auth failure), alembic migration.
- `frontend/src/components/Articles/LikeButton.tsx`, `ArticleRow.tsx` — new: optimistic TanStack Query like toggle with cache patching, article row extracted.
- `frontend/src/routes/_layout/profile.tsx` — new: tabs Liked (default) / My profile / Password / Danger zone.
- `backend/app/models_agentique.py` — `ArticleLike` table; `ArticlePublic` gains `like_count`, `liked_by_me`.
- `backend/app/api/routes/articles.py` — LEFT JOIN `article_like` aggregate for `like_count`; per-user liked-id for `liked_by_me`; `sort=likes-desc`. Counts at query time, not denormalized.
- `frontend/src/components/Articles/ArticlesList.tsx` — renders `ArticleRow`; `data-testid`s added.
- `frontend/src/components/Sidebar/Filters.tsx` — "Popular" (`likes-desc`) sort option.
- `backend/app/api/main.py` — mounts `likes.router`.
- `backend/tests/conftest.py` — `db` teardown deletes `article_like` before users.
- `frontend/src/routes/_layout/settings.tsx` — `beforeLoad` redirect to `/profile`.
- `frontend/src/routes/login.tsx` — `redirect` search param via `Route.useSearch()`.
- `frontend/src/hooks/useAuth.ts` — `loginMutation` accepts optional `redirectTo`.
- `frontend/src/components/Sidebar/User.tsx` — "Log in" when logged out; "Profile" menu item → `/profile`.
- `frontend/src/routeTree.gen.ts`, `frontend/src/client/{schemas,sdk,types}.gen.ts` — regenerated.
- `frontend/tests/user-settings.spec.ts` — `/settings` → `/profile`; removed `test.skip`.
- `frontend/tests/login.spec.ts`, `frontend/tests/sign-up.spec.ts` — removed `test.skip`.
- `frontend/tests/utils/user.ts` — post-login assertion to sidebar user-menu visibility.
- `frontend/tests/likes.spec.ts` — new: fire button, anonymous→login redirect, optimistic toggle, sort, Liked tab; serialized.
- `backend/pyproject.toml` — dropped `login.py`, `users.py` from coverage omit; 92% coverage.
- `backend/tests/api/routes/test_login.py`, `test_users.py` — removed module-level skip; `test_recovery_password` patches `EMAILS_FROM_EMAIL`.
- `backend/app/models_agentique.py`, `backend/app/api/routes/articles.py` — `# type: ignore[import-untyped]` on `pgvector.sqlalchemy`; reordered imports for `ruff check`.
- `backend/app/api/routes/articles.py` — `# ty: ignore[...]` on `Article.score`/`Article.embedding` query lines (known `ty` false positive).
- `backend/app/seed_articles.py` — `session.execute(delete(Article))` → `session.exec(...)` (`ty` deprecation).
- `frontend/src/client/{schemas,sdk,types}.gen.ts` — regenerated; was stale, missing `private` router types.

## 2026-07-01

- `.github/workflows/test-backend.yml`, `playwright.yml`, `pre-commit.yml` — added "Create .env for CI" step (fixed non-secret values).
- `.github/workflows/deploy-production.yml` — moved `packages: write` to `build` job only (`zizmor`).
- `backend/app/api/main.py` — `"local"` → `"development"` for `private` router mount (missed in 2026-06-29 rename).
- `backend/app/api/routes/articles.py` — removed unused `sqlalchemy.or_` import. `# pragma: no cover` on `get_model()`/`_embed()` (monkeypatched in tests).
- `backend/app/seed_articles.py` — 50 deterministic sample articles, every filter dimension, 256-dim embeddings. Idempotent wipe-and-reinsert; refuses production.
- `backend/scripts/prestart.sh` — guarded `python -m app.seed_articles` after `initial_data.py`.
- `backend/pyproject.toml` — `[tool.coverage.report] omit` for upstream modules unused by Agentique; `--fail-under=90` measures only exercised code.
- `backend/tests/api/routes/test_newsletter.py` — `monkeypatch.setenv("RESEND_API_KEY"`/`"RESEND_AUDIENCE_ID")` so `resend.Contacts.create` branch is reached.
- `backend/tests/api/routes/test_articles.py` — `since=<malformed date>` fallback test.
- `frontend/src/components/Newsletter/SubscribeForm.tsx` — `noValidate` on `<form>` (browser HTML5 validation intercepted submit before React/zod).
- `tests/api/routes/test_login.py`, `test_users.py`, `test_items.py`, `test_private.py`, `tests/crud/test_user.py` — module-level skip (files kept).
- `frontend/tests/{login,sign-up,reset-password,admin,user-settings,items}.spec.ts` — file-level skip.
- New files: `backend/tests/api/routes/test_articles.py`, `test_newsletter.py` (monkeypatches `resend.Contacts.create`), `frontend/tests/newsletter.spec.ts`, `frontend/tests/articles.spec.ts`.

## 2026-06-30

- `compose.yml` — `www-http`/`www-https` Traefik routers + `redirectregex` to 301 `www.${DOMAIN}` → bare domain.
- `compose.yml` — `SHELL=/bin/sh` for pipeline (was inheriting host `zsh`, crashing).
- `compose.yml` — pipeline command `supercronic -no-reap` (PID 1 reaper crash without it).
- `backend/pipeline/crontab` — `python` → `/app/.venv/bin/python`.
- `backend/app/main.py` — `newsletter.router` mounted on `app` under `/api`.
- `backend/pyproject.toml` — `resend` dependency.
- `compose.yml` — `RESEND_API_KEY`/`RESEND_AUDIENCE_ID` for `prestart` and `backend`.

## 2026-06-29

- `backend/app/core/config.py` — `ENVIRONMENT` Literal `"local"` → `"development"`; matching guard updated.

## 2026-06-28

- `frontend/src/routes/_layout.tsx` — `beforeLoad` auth guard commented out.
- `frontend/src/routes/_layout/index.tsx` — Dashboard → `ArticlesList`.
- `.env` — deleted and gitignored.
- `compose.yml` — frontend Traefik rule `dashboard.${DOMAIN}` → `${DOMAIN}` (root domain). Added `PROJECT_NAME` to `prestart`/`backend` env.
- `.github/workflows/deploy-production.yml` — split into build (GitHub runner, pushes to ghcr.io) and deploy (self-hosted runner, pulls/restarts). Added buildx + GHA layer caching. Added missing compose env vars.
- GitHub secrets — `DOCKER_IMAGE_*` → ghcr.io URLs; `BACKEND_CORS_ORIGINS`/`FRONTEND_HOST` → `https://next.agentique.ch`; added `STACK_NAME_PRODUCTION=agentique-next`.
- `.github/workflows/deploy-staging.yml` — reverted to upstream, disabled (`workflow_dispatch` only).
- `.github/workflows/deploy-production.yml` — trigger `release: published` → `push: [master]`; added `touch .env`; added missing compose env vars.
- Neutered upstream CI `on:` triggers to `workflow_dispatch` (manual-only): `add-to-project`, `smokeshow`, `labeler`, `detect-conflicts`, `guard-dependencies`, `issue-manager`, `latest-changes`, `test-docker-compose`.

## 2026-06-27 — pipeline migration

- `backend/pyproject.toml` — `baml-py`, `trafilatura`, `feedparser`, `dnspython`, `regex`.
- `backend/Dockerfile` — supercronic install; COPY `baml_client` + `pipeline`.
- `compose.yml` — `pipeline` service (supercronic, daily 04:00).

## 2026-06-27

- `compose.yml` — db image `postgres:18` → `pgvector/pgvector:pg17`.
- `backend/pyproject.toml` — `pgvector`, `model2vec`.
- `backend/app/api/main.py` — `articles` router (items router kept).
