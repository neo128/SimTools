# Contributing

Thanks for helping with SimTools. The project is a lightweight metamanager for
embodied AI simulation tools, not a monolithic simulator installer.

## Start Here

1. Read `AGENTS.md`.
2. Read the relevant docs under `docs/`.
3. Use project-local workflows under `prompts/superpowers/` when they match the
   task.
4. Keep changes small and reviewable.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,dashboard]"
./scripts/validate_project.sh
```

## Rules

- Do not install real simulators in the base SimTools environment.
- Do not add heavyweight simulator packages to `pyproject.toml`.
- Do not download large assets in tests.
- Do not launch GUI windows in tests.
- Do not eager import simulator packages.
- Keep install commands as explicit install plans unless a task asks for an
  isolated opt-in real validation.

## Adding a Simulator

Follow `prompts/superpowers/simtools-add-adapter/SKILL.md`.

Minimum work:

1. Add `configs/tools/<tool_id>.yaml`.
2. Add `src/simtools/adapters/<tool_id>.py`.
3. Add or update adapter contract tests.
4. Update `docs/07_TOOL_MATRIX.md`.
5. Update `docs/08_INSTALLATION_PROFILES.md`.
6. Run `./scripts/validate_project.sh`.

## Pull Request Checklist

- `pytest` passes.
- `python -m simtools validate` passes.
- CLI commands touched by the change were verified.
- No heavy simulator imports at module import time.
- Docs and README are updated when behavior changes.
