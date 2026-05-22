# Superpowers Workflow

SimTools uses Superpowers as a development discipline layer, not as a runtime
dependency. The repository remains governed by `AGENTS.md`; project-local
Superpowers-style workflows live under `prompts/superpowers/`.

## Available Project Workflows

| Workflow | Use When |
| --- | --- |
| `prompts/superpowers/simtools-add-adapter/SKILL.md` | Adding a new simulator, benchmark, or environment suite |
| `prompts/superpowers/simtools-review-harden/SKILL.md` | Reviewing or stabilizing docs, CLI, manifests, adapters, or tests |

## How to Use

1. Read `AGENTS.md`.
2. If a project workflow matches the task, read its `SKILL.md`.
3. Read the required docs listed by that workflow.
4. Update `plans/` for multi-step work.
5. Implement the smallest useful change.
6. Run the workflow's verification commands.
7. Summarize only claims backed by fresh verification output.

For whole-project hardening, include:

```bash
python -m simtools status
python -m simtools profiles
python -m simtools artifacts
python -m simtools validate
```

## Superpowers Fit

- Use `brainstorming` before vague design work.
- Use `writing-plans` for multi-stage changes.
- Use `test-driven-development` for behavior changes.
- Use `systematic-debugging` for failing tests or CLI regressions.
- Use `verification-before-completion` before claiming the work is complete.
- Use `finishing-a-development-branch` when preparing integration choices.

## SimTools-Specific Rule

Superpowers workflows must serve the SimTools constraints. They must not bypass
the repository's ban on automatic heavy simulator installation, large downloads,
GUI launches in tests, or eager imports of simulator packages.
