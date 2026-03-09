# Coding Standards

> Agreed-upon code quality standards for AI agents to apply consistently across this project.

## Python Standards

**Runtime**: Python 3.10+, managed with `uv`

**Linting and formatting**: `ruff` — run `uv run ruff check .` and `uv run ruff format .`
**Type checking**: `ty` — run `uv run ty check`

**Naming**:
- Modules, functions, variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

**Type annotations**: Required on all non-trivial public functions and methods. Use `from __future__ import annotations` for forward references.

**Import order** (enforced by ruff):
1. Standard library
2. Third-party packages
3. Local application imports

No relative imports (`..`) — use absolute imports only.

**Function size**: Max 100 lines, cyclomatic complexity ≤ 8, max 5 positional parameters.

**Docstrings**: Google-style on non-trivial public APIs. Code should be self-documenting — only add docstrings where the purpose isn't obvious from names and types.

## TypeScript Standards

**Runtime**: Node 22, ESM-only (`"type": "module"` in package.json)
**Package manager**: `bun`

**Linting and formatting**: `oxlint` and `oxfmt`

**tsconfig.json** — enable all strictness flags:
- `strict: true`
- `noUncheckedIndexedAccess: true`
- `exactOptionalPropertyTypes: true`
- `noImplicitOverride: true`
- `noPropertyAccessFromIndexSignature: true`
- `verbatimModuleSyntax: true`
- `isolatedModules: true`

**Naming**:
- Variables, functions: `camelCase`
- Classes, types, interfaces: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Files: `kebab-case.ts`

No relative imports (`../`) across package boundaries — use absolute imports configured via `tsconfig.json` paths.

**Test files**: Colocated as `*.test.ts` alongside source files.

## Testing Principles

**Test behavior, not implementation.** Tests verify what the code does, not how. A refactor that doesn't change behavior must not break tests.

**Test edges and errors, not just the happy path.** Empty inputs, boundary values, malformed data, missing files — bugs live in edges. Every error path the code handles should have a test that triggers it.

**Mock only boundaries.** Mock things that are slow (network, filesystem), non-deterministic (time, randomness), or external services you don't control. Never mock internal application logic.

**Verify tests catch failures.** Break the code, confirm the test fails, then fix. Tests that always pass regardless of implementation are useless.

## Error Handling

**Fail fast with clear, actionable messages.** When something goes wrong, raise immediately with context: what operation failed, what input caused it, and what the caller should do.

**Never swallow exceptions silently.** No bare `except: pass` or `.catch(() => {})`. If an error is genuinely ignorable, add a comment explaining why.

**Include context in error messages**: what operation was attempted, what the unexpected value was, and a suggested fix where possible.

## Comments

**Code should be self-documenting.** Choose names that make the purpose obvious. If a comment explains what the code does, the code probably needs refactoring.

**No commented-out code.** Delete it. Version control exists to recover deleted code.

**Comments explain why, not what.** The only valid use for a comment is to explain a non-obvious decision, a known limitation, or a gotcha that the code cannot express.

**No `<!-- TODO -->` comments in rule files.** Open items go to `tasks.md`.
