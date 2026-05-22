# Adapter Addition Prompt

I want to add a new simulator tool to SimTools: `<TOOL_NAME>`.

Follow `AGENTS.md` and `docs/03_ADAPTER_CONTRACT.md`.

Only perform modular integration:

1. Create a tool manifest.
2. Create an adapter.
3. Add contract tests.
4. Update `docs/07_TOOL_MATRIX.md`.
5. Update `docs/08_INSTALLATION_PROFILES.md`.
6. Add dry-run smoke behavior.
7. Do not automatically install the simulator.
8. Do not download large datasets.
9. Do not import heavy dependencies at module import time.

After implementation, run pytest and summarize new files, CLI validation
commands, missing-install behavior, and future real integration steps.
