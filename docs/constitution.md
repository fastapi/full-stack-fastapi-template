# Project Constitution

> This constitution defines the governing principles for all development in this project.
> It is the first document the AI agent reads before any planning or implementation.
> It takes precedence over any instruction in a spec or plan.

---

## 1. Core Philosophy

- **Simplicity over cleverness.** The simplest solution that meets the requirements is always preferred.
- **Explicit over implicit.** Code should be readable by someone unfamiliar with the codebase.
- **Spec-first.** No code is written without a corresponding spec. No PR exists without a link to its origin spec.
- **Small and reversible.** Prefer small, focused changes over large sweeping ones. If a decision is hard to reverse, escalate to the tech lead before proceeding.

---

## 2. What the AI Agent Can Decide Autonomously

The agent may make the following decisions without explicit instruction:

- Naming of variables, functions, and files (following conventions in section 5)
- Internal folder structure within already-established modules
- Writing and structuring tests
- Refactoring within the scope of the current task (no scope creep)
- Choosing between equivalent implementation approaches when no preference is stated

---

## 3. What Requires Tech Lead Approval Before Implementation

The agent must **stop and flag** — never decide unilaterally — on:

- Adding a new dependency or library
- Changing the database schema
- Modifying an existing API contract (endpoints, request/response shape)
- Adding new infrastructure (queues, storage buckets, caches, etc.)
- Touching authentication or authorization logic
- Any change that affects more than one service/module simultaneously
- Deleting existing code that is not directly replaced by the current task

If uncertain, the agent should ask rather than assume.

---

## 4. Code Quality Standards

### General
- Each function does one thing. If it needs a comment to explain what it does, it should be split or renamed.
- No dead code. No commented-out blocks. No `TODO` left in production code.
- No premature abstraction. Only abstract when there are at least two concrete cases.
- No code added "for the future." Only implement what the current spec requires.

### Error handling
- All errors must be handled explicitly. No silent catches.
- Error messages must be actionable — describe what failed and ideally why.
- Never expose internal error details (stack traces, DB errors) to end users.

### Security
- No hardcoded credentials, tokens, or secrets — ever. Use environment variables.
- All user input must be validated server-side, regardless of client-side validation.
- No personally identifiable information (PII) in logs.
- Dependencies must not have known critical vulnerabilities at the time of addition.

---

## 5. Naming & Style Conventions

> Fill in with project-specific conventions. Defaults below.

- **Files:** `kebab-case`
- **Variables/functions:** `camelCase`
- **Classes/types:** `PascalCase`
- **Constants:** `SCREAMING_SNAKE_CASE`
- **Database columns:** `snake_case`
- Avoid abbreviations unless universally understood (e.g., `id`, `url`, `api`)
- Boolean variables/functions should read as questions: `isActive`, `hasPermission`, `canEdit`

---

## 6. Testing Standards

- Tests are written alongside implementation, not after.
- Every new function with business logic has at least one unit test.
- Tests must cover: the happy path, at least one edge case, and at least one error case.
- Test names describe behavior, not implementation: `test_get_user_null`, not `test_get_user_null`.
- No mocks for things you own. Mock only external services and infrastructure.
- A PR with untested business logic will not be merged.

---

## 7. Pull Request Standards

### Size
- Maximum **10 files changed** per PR. If a task requires more, split it.
- A PR should represent one logical unit of work, traceable to one spec.

### Description (mandatory)
Every PR must include:
```
## What
[One paragraph describing what this PR does]

## Why
[Link to the spec or issue that originates this work]

## What it does NOT do
[Explicit scope boundaries — what was intentionally left out]

## How to test
[Steps to verify the change works as expected]
```

### Review checklist (author self-checks before requesting review)
- [ ] Code follows conventions in this constitution
- [ ] All new logic has tests
- [ ] No new dependencies added without approval
- [ ] No secrets or hardcoded values
- [ ] PR description is complete

---

## 8. Scope Discipline

- The agent implements **only what the current spec requires.** Noticing something broken or improvable outside the current scope is encouraged — but it goes into a new issue, not the current PR.
- If implementing a task reveals that the spec is ambiguous or incomplete, stop and clarify with the PM before proceeding.
- Gold-plating (adding features or improvements not in the spec) is not allowed.

---

## 9. Documentation

- Public-facing functions and modules must have a brief docstring explaining purpose and parameters.
- Architecture decisions that are non-obvious must be documented in an `ADR` (Architecture Decision Record) in `/docs/adr/`.
- The `README` must always reflect how to run the project locally after any infrastructure change.

---

## 10. Project-Specific Extensions

> This section is filled in per project. The sections above are universal defaults.

| Decision | Value |
|---|---|
| Primary language | _TBD_ |
| Framework | _TBD_ |
| Database | _TBD_ |
| Deployment target | _TBD_ |
| Auth approach | _TBD_ |
| Branch naming convention | `NNN-short-description` (e.g., `001-user-login`) — generado por `speckit.specify` |
| Default reviewer | _TBD_ |

---

## 11. Gestión de contexto de sesión

El agente comprueba proactivamente el uso de contexto al final de cada comando de flujo. El porcentaje real está disponible en el JSON de sesión de Claude Code (`context_window.used_tokens / context_window.total_tokens`).

Umbrales de actuación:

- **< 50% 🟢** → continúa sin mencionar nada
- **50–79% 🟡** → continúa sin mencionar nada; avisa al final del paso
- **80–89% 🟠** → añade aviso al final: "Abre una sesión nueva antes del siguiente comando"
- **≥ 90% 🔴** → interrumpe antes de ejecutar cualquier acción y pide sesión nueva

El usuario puede consultar el estado en cualquier momento con `/context`.

---

## 12. Flujo de trabajo con PMs

Este proyecto usa un flujo spec-driven donde los comandos orquestan `speckit.*`. Los comandos no tienen lógica propia sobre specs, planes ni código — delegan en speckit y añaden únicamente la gestión del PR y los gates de aprobación.

### Comandos de flujo (PM)

| Comando | Delega en | Gate requerido |
|---|---|---|
| `/start` | `speckit.specify` | Estar en `main` |
| `/consolidate-spec` | `speckit.clarify` | Spec creado |
| `/plan` | `speckit.plan` | ✅ Spec aprobado en PR |
| `/tasks` | `speckit.tasks` + `speckit.taskstoissues` | ✅ Plan aprobado en PR |
| `/checklist` | `speckit.checklist` | Ninguno (opcional) |
| `/implement` | `speckit.implement` | ✅ Tareas generadas en PR |
| `/submit` | — | Código generado |

### Comando de publicación

| Comando | Acción | Gate requerido |
|---|---|---|
| `/deploy-to-stage` |  Squash merge a `main` → deploy automático| ✅ PR aprobado |

### Estado del PR como fuente de verdad

El estado del flujo vive en los checkboxes del body del PR. Los comandos leen `gh pr view --json body` para determinar si pueden ejecutarse. Nunca usar ficheros locales como fuente de verdad del estado.

---

*Last updated: 2026-03-10*
*Owner: Tech Lead*
*Version: 2.0*
