# Security Plan — SecureNotes (Phase 1)

**Author:** [Your Full Name]
**Repo:** [https://github.com/YourGitHubUser/secure-notes](https://github.com/YourGitHubUser/secure-notes)
**Date:** YYYY-MM-DD

## 1. Summary

This plan defines security objectives, assets, roles, high-level controls, and next steps for Phase 1 of SecureNotes (FastAPI).

## 2. Security Objectives (CIA + Privacy)

* **Confidentiality**: Encrypt note bodies at rest using AES-GCM with a 256-bit application master key.
* **Integrity**: Use JWT with HMAC (HS256) and short token lifetimes; authenticated encryption for stored data.
* **Availability**: Basic rate limiting plan and graceful error handling (to be implemented).
* **Privacy**: Minimize PII; store username and password hash only; redact sensitive logs.

## 3. System Assets

| Asset                      |   Classification | Comments                               |
| -------------------------- | ---------------: | -------------------------------------- |
| Note content               |        Sensitive | Must be encrypted at rest              |
| User credentials           | Highly sensitive | Store hashed (bcrypt) only             |
| MASTER_KEY / JWT_SECRET    |           Secret | Store in GitHub Secrets/secret manager |
| Database backups           |        Sensitive | Encrypt & restrict access              |
| CI tokens & registry creds |           Secret | Least privilege in CI                  |

## 4. Users & Roles

* **User**: create/read own notes.
* **Admin** (future): manage users and system.
* **Developer/CI**: builds and tests; must not leak secrets.

## 5. Data Flows (high level)

* User → HTTPS → FastAPI endpoints (register, login, /notes)
* FastAPI → encrypt note → DB (store ciphertext)
* CI (GitHub Actions) → build/test/scan → images/reports

A Level-0 DFD diagram is included: `docs/system_overview.png` / `.pdf`.

## 6. Initial Controls to implement (Phase 2/3 plan)

1. Password hashing (bcrypt via passlib).
2. JWT auth (short lived access tokens).
3. AES-GCM encryption for note bodies (app master key from secrets).
4. Pydantic input validation for all endpoints.
5. Security headers middleware (CSP, HSTS, X-Frame-Options).
6. CI: CodeQL, Snyk (SCA), Trivy (container), OWASP ZAP (DAST).

## 7. Key risks & mitigations

* **Leak of master key** → use GitHub Secrets & rotation plan.
* **Dependency vulnerabilities** → Snyk scans and upgrades.
* **Misconfigured CI secrets** → restrict access & do not echo secrets in logs.

## 8. Phase-1 acceptance criteria

* Repo forked and branch `phase1-setup` created.
* Security Plan and DFD added to `docs/`.
* PR created (and merged).
