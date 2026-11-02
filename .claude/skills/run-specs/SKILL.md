---
name: run-specs
description: Autonomously execute every pending spec in openspec/roadmap.md with OpenSpec (branch, propose, apply, merge, archive). Use only after the roadmap has been approved by the user.
disable-model-invocation: true
allowed-tools: Bash(git:*) Bash(gh:*) Bash(openspec:*)
---

# Run approved specs (autonomous)

## Rules for the whole run

- Do not ask the user anything. Never pause for confirmation.
- When a skill or decision offers options, pick the recommended one (or the one most
  consistent with `openspec/roadmap.md`) and log it under "Decisiones" in the PR description.
- `openspec/roadmap.md` is the source of truth. Do not expand scope beyond it.
- Use the project commands defined in `CLAUDE.md` as quality gates.

## Preflight (once)

1. Confirm `openspec/roadmap.md` exists and has unchecked specs. If not, stop and report.
2. Confirm the working tree is clean and `gh auth status` succeeds. If not, stop and report.
3. `git switch main && git pull --ff-only`
4. The run resumes automatically: process only specs that are still `- [ ]`, in order.
   If a `spec/<name>` branch already exists for the next spec, continue on it instead of recreating it.

## Loop: for each unchecked spec, in order

1. **Branch**
   `git switch main && git pull --ff-only && git switch -c spec/<spec-name>`

2. **Propose**
   Run the OpenSpec propose skill (e.g. `/opsx:propose`) for this spec, using its goal and
   acceptance criteria from the roadmap. Check the proposal against the roadmap's guidelines and
   out-of-scope list. Commit: `docs(<spec-name>): agregar propuesta de OpenSpec`.

3. **Apply**
   Run the OpenSpec apply skill (e.g. `/opsx:apply`) and complete every task.
   Write or update tests that cover the acceptance criteria.
   Run test, lint and build. Fix failures (maximum 2 fix attempts).
   Commit in logical steps with Spanish descriptions: `feat(<spec-name>): ...`, `test(<spec-name>): ...`.

4. **Merge**
   ```
   git push -u origin spec/<spec-name>
   gh pr create --base main --title "feat: <spec-name>" --body "<en español: Resumen, Criterios de aceptación cumplidos, Decisiones>"
   gh pr checks --watch        # skip if the repo has no CI
   gh pr merge --squash --delete-branch
   ```

5. **Archive**
   `git switch main && git pull --ff-only`, then run the OpenSpec archive skill
   (e.g. `/opsx:archive`) for this change.
   Mark the spec as done in `openspec/roadmap.md` (`- [x]`).

6. **Commit archive**
   `git add -A && git commit -m "chore(<spec-name>): archivar cambio de OpenSpec" && git push`

7. Report one line (`✓ <spec-name> fusionada y archivada`) and continue with the next spec.

## Stop conditions (stop, report, never guess)

Stop the run and write a short report (spec, step, what failed, what you tried, suggested fix) when:

- Tests, lint, build or CI still fail after 2 fix attempts
- A merge conflict is not trivially resolvable
- The spec or its proposal contradicts the roadmap, or completing it needs a scope change
- A push or merge is rejected (branch protection, permissions)
- Completing a step would require a destructive action (force-push, history rewrite,
  deleting unrelated branches or data)

Leave the repo in a resumable state: work committed on the spec branch, roadmap unchanged for that spec.

## Final report

When no unchecked specs remain: list merged specs, PR links, and every logged decision.
