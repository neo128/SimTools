# SimTools Project Brief

SimTools is a local, config-driven management layer for embodied AI simulation
tools. It manages metadata, installation profiles, launch plans, smoke tests,
viewer commands, artifacts, and comparison matrices across multiple simulators.

Current tools:

- Habitat
- AI2-THOR
- ManiSkill
- BEHAVIOR-1K
- OmniGibson
- MolmoSpaces
- RoboCasa365

SimTools is not a simulator and is not a monolithic installer. It is a
metamanager that keeps each simulator isolated behind a manifest, adapter, and
profile.

## v0.1 Goal

Build a reproducible local metamanager MVP:

- project documentation and constraints
- typed manifest schema
- registry loaded from YAML manifests
- lightweight CLI
- adapter stubs
- dashboard MVP
- status, profile, artifact, install-plan, and validation views
- tests that pass without real simulators installed

## Non-goals

- installing all simulators into one Python environment
- downloading large assets
- launching GUI windows in tests
- assuming GPU availability
- running system package managers
