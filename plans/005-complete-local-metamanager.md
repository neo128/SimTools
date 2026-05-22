# Plan 005: Complete Local Metamanager MVP

## Goal

Finish the feasible SimTools project goal under `AGENTS.md`: a lightweight,
config-driven local management platform for embodied AI simulators.

## Scope

In scope:

- unified status view
- environment profile listing
- artifact listing and smoke report storage
- manifest/profile/adapter validation
- dashboard data for profiles and artifacts
- docs and tests for the complete local management surface

Out of scope:

- automatic simulator installation
- large dataset or asset downloads
- GUI launch in tests
- merging all simulator dependencies into one environment

## Verification

```bash
pytest
python -m simtools --help
python -m simtools list
python -m simtools status
python -m simtools profiles
python -m simtools compare
python -m simtools doctor
python -m simtools doctor ai2thor
python -m simtools doctor habitat
python -m simtools install-plan
python -m simtools install-plan ai2thor
python -m simtools run ai2thor --mode smoke --dry-run
python -m simtools run habitat --mode smoke --dry-run
python -m simtools view ai2thor --dry-run
python -m simtools artifacts
python -m simtools validate
python -m simtools ui --help
```

or:

```bash
./scripts/validate_project.sh
```
