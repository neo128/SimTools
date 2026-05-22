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
python -m simtools compare
python -m simtools doctor
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

## Add a New Tool

1. Add `configs/tools/<tool_id>.yaml`
2. Add `src/simtools/adapters/<tool_id>.py`
3. Add tests
4. Update `docs/07_TOOL_MATRIX.md`
5. Update `docs/08_INSTALLATION_PROFILES.md`

## Current Status

This is the v0.1 scaffold. The registry, CLI, manifests, adapter stubs, tests,
and dashboard skeleton are present. AI2-THOR has the first opt-in real adapter
path, but SimTools does not automatically install it.
