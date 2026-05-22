# AI Agent Workflow

1. Read `AGENTS.md`.
2. Read the relevant docs for the target change.
3. Check repository state with `git status` when a git repository exists.
4. Update a plan under `plans/` for multi-step work.
5. Implement the smallest useful slice.
6. Run focused tests, then the full test suite.
7. Verify CLI commands that correspond to the change.
8. Review the diff.
9. Summarize changes, risks, and next steps.

## Guardrails

- Keep simulator dependencies out of the base environment.
- Prefer manifests over hardcoded simulator data.
- Prefer adapters over CLI branches.
- Prefer dry-run plans over automatic installs.
- Keep tests deterministic and offline.
