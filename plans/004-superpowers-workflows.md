# Plan 004: Superpowers Workflows

## Goal

Add project-local Superpowers-style workflows that help future agents follow
SimTools' constraints consistently.

## Scope

In scope:

- document how Superpowers maps to SimTools development
- add an adapter-addition workflow
- add a review/harden workflow
- link workflows from `AGENTS.md`, README, and AI workflow docs
- verify CLI and tests still work

Out of scope:

- installing global skills
- installing or launching real simulators
- adding new runtime dependencies
- changing simulator adapter behavior

## Verification

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
python -m simtools ui
```

## Status

Implemented as project-local workflow documentation under
`prompts/superpowers/`.
