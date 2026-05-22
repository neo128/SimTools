---
name: simtools-add-adapter
description: Use when adding a new simulator, benchmark, environment suite, or simulator-family registry entry to SimTools
---

# SimTools Add Adapter

## Purpose

Add simulators through SimTools' manifest + adapter architecture without turning
the base package into an installer or dependency bundle.

## Required Reading

Read these before editing:

- `AGENTS.md`
- `docs/01_CONSTRAINTS.md`
- `docs/03_ADAPTER_CONTRACT.md`
- `docs/04_CONFIG_SCHEMA.md`
- `docs/07_TOOL_MATRIX.md`
- `docs/08_INSTALLATION_PROFILES.md`

## Workflow

1. Create `configs/tools/<tool_id>.yaml`.
2. Create `src/simtools/adapters/<tool_id>.py`.
3. Register the adapter through the manifest `adapter.module` and
   `adapter.class_name` fields.
4. Add or update tests in `tests/test_adapters_contract.py`.
5. Update `docs/07_TOOL_MATRIX.md`.
6. Update `docs/08_INSTALLATION_PROFILES.md`.
7. Add dry-run smoke and viewer commands.
8. Run verification commands.

## Hard Rules

- Do not install the simulator.
- Do not download datasets, assets, model weights, scenes, or external runtimes.
- Do not launch GUI viewers in tests.
- Do not add heavy simulator dependencies to `pyproject.toml`.
- Do not import heavy packages at module import time.
- Use `importlib.util.find_spec()` for package presence checks.
- Missing simulator packages must produce `skipped` or `planned` status, not
  traceback-heavy failures.
- Artifacts must stay under `.simtools/artifacts/<tool_id>/`.

## Adapter Behavior

Each adapter must implement:

- `metadata()`
- `check_installed()`
- `doctor()`
- `smoke()`
- `launch_viewer()`
- `sample_commands()`

Before a real integration exists, inherit from `ManifestOnlyAdapter` and keep
the behavior dry-run friendly.

## Verification

Run at least:

```bash
pytest
python -m simtools list
python -m simtools info <tool_id>
python -m simtools doctor <tool_id>
python -m simtools run <tool_id> --mode smoke --dry-run
python -m simtools view <tool_id> --dry-run
```

When no real simulator is installed, the expected behavior is:

- `doctor` reports missing package checks.
- `smoke --dry-run` reports a plan.
- real `smoke` skips unless a safe opt-in implementation exists.
- tests pass without the real simulator.
