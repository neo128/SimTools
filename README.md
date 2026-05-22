# SimTools

SimTools is a local management and comparison platform for embodied AI
simulation tools.

It provides:

- tool registry
- simulator metadata
- install profiles
- adapter-based launchers
- smoke tests
- local dashboard
- comparison matrix
- artifact/log management

## Supported Tools

Initial registry:

- AI2-THOR
- Habitat
- BEHAVIOR-1K
- OmniGibson
- MolmoSpaces
- RoboCasa365

## Design

SimTools does not install all simulators into one environment.

Each simulator is represented by:

1. a YAML manifest
2. an adapter
3. an install profile
4. smoke commands
5. documentation

The base package remains lightweight. Real simulator installation, large asset
downloads, GUI viewers, and GPU-specific smoke tests are all opt-in.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,dashboard]"
python -m simtools list
python -m simtools status
python -m simtools compare
python -m simtools doctor
python -m simtools validate
```

For local development without installing the package, use:

```bash
python -m simtools list
```

The repository includes a tiny root-level `simtools` shim so `python -m simtools`
works from an uninstalled checkout while the package code remains under `src/`.

## Dashboard

```bash
simtools ui
```

If Streamlit is not installed, the command prints an installation hint instead
of failing with a traceback.

## AI2-THOR Validation

AI2-THOR is validated in an isolated environment, not in the base SimTools
environment:

```bash
conda create -p ./.venv-ai2thor python=3.11 pip -y
.venv-ai2thor/bin/python -m pip install -e . ai2thor
./scripts/validate_ai2thor.sh
```

See `docs/13_AI2THOR_VALIDATION.md` for the latest local result.

## Core Commands

```bash
python -m simtools list
python -m simtools info ai2thor
python -m simtools status
python -m simtools profiles
python -m simtools compare
python -m simtools doctor
python -m simtools doctor ai2thor
python -m simtools install-plan
python -m simtools install-plan ai2thor
python -m simtools run ai2thor --mode smoke --dry-run
python -m simtools view ai2thor --dry-run
python -m simtools artifacts
python -m simtools validate
```

`run` writes non-dry-run reports under `.simtools/artifacts/<tool_id>/`.

To run the local verification suite:

```bash
./scripts/validate_project.sh
```

## Add a New Tool

1. Add `configs/tools/<tool_id>.yaml`
2. Add `src/simtools/adapters/<tool_id>.py`
3. Add tests
4. Update `docs/07_TOOL_MATRIX.md`
5. Update `docs/08_INSTALLATION_PROFILES.md`

For AI-agent assisted additions, follow:

```text
prompts/superpowers/simtools-add-adapter/SKILL.md
```

## Superpowers Workflows

Project-local Superpowers-style workflows live under `prompts/superpowers/`.
They are development guides, not runtime dependencies.

- Use `simtools-add-adapter` for new simulator integrations.
- Use `simtools-review-harden` before continuing major feature work or merging.

See `docs/11_SUPERPOWERS_WORKFLOW.md` for the current mapping.

## Current Status

This is a complete local metamanager MVP. The registry, CLI, manifests, adapter
stubs, tests, artifact listing, profile listing, validation, and dashboard MVP
are present. AI2-THOR has the first opt-in real adapter path, but SimTools does
not automatically install it.
