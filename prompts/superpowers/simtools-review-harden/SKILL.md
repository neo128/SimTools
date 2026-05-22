---
name: simtools-review-harden
description: Use when reviewing or stabilizing the SimTools scaffold, CLI, docs, manifests, adapters, or tests before continuing feature work
---

# SimTools Review Harden

## Purpose

Find and fix scaffold drift while preserving SimTools' core boundary: a
lightweight metamanager, not a heavyweight simulator installer.

## Required Reading

Read these before changing files:

- `AGENTS.md`
- `docs/01_CONSTRAINTS.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_ADAPTER_CONTRACT.md`
- `docs/04_CONFIG_SCHEMA.md`
- `docs/05_CLI_SPEC.md`
- `docs/06_DASHBOARD_SPEC.md`
- `docs/10_ROADMAP.md`

## Review Checklist

- Docs and code describe the same architecture.
- All tool metadata comes from `configs/tools/*.yaml`.
- CLI and dashboard use the same registry/config path.
- No CLI command hardcodes simulator-specific behavior that belongs in an
  adapter.
- Adapters do not eager import heavy simulator packages.
- Tests do not require real simulators, GUI windows, large assets, GPU, or
  network downloads.
- Install plans print commands only.
- Missing simulator packages return useful `missing`, `planned`, or `skipped`
  responses.
- Artifacts are repository-local under `.simtools/`.
- README contains a fresh quick start and current limitations.

## Commands

Run the full verification set:

```bash
pytest
python -m simtools --help
python -m simtools list
python -m simtools compare
python -m simtools doctor
python -m simtools doctor ai2thor
python -m simtools install-plan ai2thor
python -m simtools run ai2thor --mode smoke
python -m simtools view ai2thor --dry-run
python -m simtools ui --help
```

If Streamlit is not installed, `python -m simtools ui` should print an
installation hint instead of starting a process or failing with a traceback.

## Red Flags

- `import ai2thor`, `import habitat`, `import omnigibson`, `import mujoco`, or
  similar at module import time.
- `pip install`, `conda install`, `apt`, `brew`, or `sudo` executed by tests or
  default CLI paths.
- tests that depend on external assets or GPU state.
- documentation promising real integrations that are still dry-run stubs.

## Completion

Before reporting success, apply the Superpowers verification-before-completion
rule: state only what was freshly verified, with command evidence.
