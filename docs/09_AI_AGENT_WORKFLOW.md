# AI Agent Workflow

1. Read `AGENTS.md`.
2. If a matching project workflow exists under `prompts/superpowers/`, read it.
3. Read the relevant docs for the target change.
4. Check repository state with `git status` when a git repository exists.
5. Update a plan under `plans/` for multi-step work.
6. Implement the smallest useful slice.
7. Run focused tests, then the full test suite.
8. Verify CLI commands that correspond to the change.
9. Review the diff.
10. Summarize changes, risks, and next steps.

## Project Superpowers Workflows

- `prompts/superpowers/simtools-add-adapter/SKILL.md`: use when adding a new
  simulator, benchmark, or environment suite.
- `prompts/superpowers/simtools-review-harden/SKILL.md`: use when reviewing or
  stabilizing docs, CLI, manifests, adapters, tests, or README.

These are project-local workflows. They must follow `AGENTS.md` and the
constraints in `docs/01_CONSTRAINTS.md`.

## Guardrails

- Keep simulator dependencies out of the base environment.
- Prefer manifests over hardcoded simulator data.
- Prefer adapters over CLI branches.
- Prefer dry-run plans over automatic installs.
- Keep tests deterministic and offline.
- Verify before completion: cite fresh command output before claiming a task is
  complete or passing.
