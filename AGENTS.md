# AGENTS.md

## Project

This repository is `SimTools`, a local simulator management and comparison
platform for embodied AI simulation tools.

The project manages tools such as:

- Habitat
- AI2-THOR
- ManiSkill
- BEHAVIOR-1K
- OmniGibson
- MolmoSpaces
- RoboCasa365

It must remain modular so future simulators can be added without rewriting the
core system.

## Prime Directive

Build SimTools as a modular, config-driven, adapter-based local management
platform.

Do not implement heavyweight simulator installation directly in the core
package. The core package must remain lightweight and testable without any real
simulator installed.

## Architecture Rules

- Use a manifest + adapter architecture.
- Every simulator tool must have a YAML manifest under `configs/tools/`.
- Every simulator tool must have an adapter under `src/simtools/adapters/`.
- Adapters must lazy import heavy dependencies.
- The core registry must work even when no simulator is installed.
- CLI and UI must read from the same registry and config models.
- No simulator-specific logic should be hardcoded into CLI commands.
- Adding a new simulator should require:
  1. one manifest
  2. one adapter
  3. one adapter contract test
  4. one documentation update

## Do Not Rules

- Do not run `sudo`.
- Do not automatically install system packages.
- Do not download large datasets during tests.
- Do not launch GUI windows during tests.
- Do not assume NVIDIA GPU availability.
- Do not import AI2-THOR, Habitat, OmniGibson, MuJoCo, or other heavy libraries
  at module import time.
- Do not mix all simulator dependencies into the base SimTools environment.
- Do not write files outside the repository or `.simtools/` unless explicitly
  requested.
- Do not remove or rewrite documentation without preserving intent.

## Preferred Tech Stack

- Python 3.11+
- Typer for CLI
- Rich for terminal output
- Pydantic v2 for typed models
- PyYAML for config loading
- pytest for tests
- Streamlit for local dashboard MVP

## Repository Layout

- `configs/`: global config, profiles, and tool manifests
- `docs/`: architecture, constraints, adapter contract, CLI/UI specs
- `plans/`: execution plans for AI agents
- `prompts/`: reusable prompts for Codex and other agents
- `prompts/superpowers/`: project-local Superpowers-style workflows
- `src/simtools/`: Python package
- `tests/`: unit tests that do not require real simulators
- `scripts/`: local development helpers

## Commands

Use these commands after implementation:

```bash
python -m simtools --help
python -m simtools list
python -m simtools status
python -m simtools compare
python -m simtools doctor
python -m simtools validate
pytest
```

If a Makefile exists:

```bash
make test
make lint
make typecheck
```

## Testing Rules

- Write unit tests for config loading, registry, capability matrix, and adapter
  contracts.
- Tests must pass without AI2-THOR, Habitat, ManiSkill, OmniGibson,
  MolmoSpaces, RoboCasa365, or BEHAVIOR-1K installed.
- Use fake manifests and fake adapters for contract tests.
- Real simulator smoke tests must be opt-in and skipped by default when the
  simulator is not installed.

## Documentation Rules

Before implementing major code, update or create:

- `docs/01_CONSTRAINTS.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_ADAPTER_CONTRACT.md`
- `docs/04_CONFIG_SCHEMA.md`
- `docs/05_CLI_SPEC.md`

Every new adapter must update:

- `docs/07_TOOL_MATRIX.md`
- `docs/08_INSTALLATION_PROFILES.md`

## Done Criteria

A task is complete only when:

1. Code is implemented.
2. Docs are updated.
3. Tests are added or updated.
4. `pytest` passes.
5. CLI still starts.
6. No heavy simulator is imported in base tests.
7. The change is summarized with risks and follow-up tasks.

## AI Agent Workflow

For complex work:

1. Read `AGENTS.md`.
2. If a matching project workflow exists, read it under `prompts/superpowers/`.
3. Read relevant docs in `docs/`.
4. Create or update a plan in `plans/`.
5. Implement the smallest useful slice.
6. Run tests.
7. Review the diff.
8. Summarize changes, risks, and next steps.

Prefer small, reviewable commits.

## Superpowers Workflow Hooks

Project-local Superpowers-style workflows live in `prompts/superpowers/`.
They are reference workflows for AI agents; they are not runtime dependencies.

- Use `prompts/superpowers/simtools-add-adapter/SKILL.md` when adding a new
  simulator or benchmark integration.
- Use `prompts/superpowers/simtools-review-harden/SKILL.md` when reviewing,
  hardening, or stabilizing the scaffold.
- Use Superpowers-style verification before completion: do not claim tests,
  CLI commands, or scaffold checks pass unless they were freshly run and read.
