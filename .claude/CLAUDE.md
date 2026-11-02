# CLAUDE.md

This project is built with **OpenSpec** using a two-phase workflow.
The human is involved **only in Phase 1 (exploration)**. Everything after that is autonomous.

## Project commands

Fill these in once; the `run-specs` skill uses them as quality gates.

- Install: `uv sync`
- Test: `docker compose up -d --wait && uv run pytest`
- Lint: `uv run ruff check . && uv run ruff format --check .`
- Build: `none`
- Default branch: `main`

If a command is still a placeholder, detect it from the repo (package.json, Makefile,
pyproject.toml, etc.) and write the detected value here in the same commit as your first change.

## Phase 1: Exploration (HUMAN-IN-THE-LOOP)

Goal: leave no ambiguity for Phase 2, because proposals are not reviewed by a human.

- Use the OpenSpec explore skill (e.g. `/opsx:explore`) to define, together with the user:
  - project objectives and scope (including what is explicitly out of scope)
  - guidelines: stack, architecture, conventions, testing expectations
  - an ordered list of specs, each with concrete acceptance criteria and dependencies
- Ask questions freely and wait for answers. Do NOT propose, apply or write code in this phase.
- Record the result in `openspec/roadmap.md` using this format:

  ```markdown
  # Roadmap
  ## Objectives
  ## Guidelines
  ## Out of scope
  ## Specs (execute in order)
  - [ ] `spec-name` — one-line goal
    - Acceptance: ...
    - Depends on: ...
  ```

- Phase 1 ends only when the user explicitly approves the roadmap. Then commit and push it:
  `docs: agregar roadmap aprobado de OpenSpec`.

## Phase 2: Execution (AUTONOMOUS)

Triggered by `/run-specs`. Follow the `run-specs` skill exactly.

- Never ask the user for confirmation or input. Do not use question/choice prompts.
- When any skill or decision presents options, choose the recommended one
  (or the one most consistent with `openspec/roadmap.md`) and record it in the PR description.
- `openspec/roadmap.md` is the source of truth for scope and guidelines.
- Only the stop conditions in the skill may interrupt the run.

## Always

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`), with the
  description in Spanish. Everything in this project is written in Spanish (see `openspec/roadmap.md`).
- Never force-push, rewrite history, or delete branches other than a just-merged spec branch.
- Never commit secrets or `.env` files.
