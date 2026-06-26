---
name: library-skills
description: Use Library Skills to discover, install, refresh, repair, check, and manage agent skills from installed packages.
---

# Library Skills

Use this skill when a project might benefit from agent skills bundled by its installed packages, or when existing Library Skills-managed symlinks are stale, broken, orphaned, or need to be checked.

Run commands from the project root.

Agents bundle their own skills by including an `.agents/skills` directory. More details in [Library Skills](https://library-skills.io).

## First-Time Setup

- Make sure project dependencies are installed first, for example with `uv sync` for Python projects or `npm install` / `bun install` for Node.js projects.
- Run `uvx library-skills` or `npx library-skills` to discover skills bundled by the installed packages and install selected skills interactively.
- Use `uvx library-skills --all` or `npx library-skills --all` only when all newly discovered skills should be installed without selecting individual skills.
- Use `uvx library-skills --tool-skill` or `npx library-skills --tool-skill` to copy this Library Skills tool skill into the project so future agents know how to discover, install, update, repair, and check skills.

## Commands

- Run `uvx library-skills` or `npx library-skills` to discover package-provided skills, install selected new skills, and reconcile existing managed symlinks.
- Run `uvx library-skills list` or `npx library-skills list` to inspect discovered and installed skills.
- Run `uvx library-skills list --json` or `npx library-skills list --json` for machine-readable installed status.
- Run `uvx library-skills scan --json` or `npx library-skills scan --json` for discovery-only automation.
- Run `uvx library-skills --check` or `npx library-skills --check` to validate managed skill symlink state without changing files.
- Run `uvx library-skills --yes` or `npx library-skills --yes` to repair stale managed symlinks and remove orphaned managed symlinks non-interactively.
- Add `--claude` when `.claude/skills` should also be managed.
- Add `--skill NAME` to install a specific discovered skill by name.

## Safety

- Prefer rerunning `library-skills` over editing managed symlinks manually.
- If installed skill symlinks are broken, dependencies may not be installed yet. Try the project's normal install command first, such as `uv sync`, `npm install`, or `bun install`, then rerun `library-skills`.
- Do not delete or overwrite hand-authored skill directories.
- Library Skills only removes managed symlinks. It should not remove copied or hand-authored skill directories.
