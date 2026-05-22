# Release Checklist

Use this checklist before tagging or publishing a SimTools release.

## Local Checks

```bash
./scripts/validate_project.sh
git diff --check
```

## Constraint Checks

- No heavyweight simulator dependencies in `pyproject.toml`.
- No eager imports of AI2-THOR, Habitat, OmniGibson, MuJoCo, RoboCasa, or
  BEHAVIOR-1K packages.
- No tests download large assets.
- No tests launch GUI viewers.
- Install plans print commands only.
- Artifacts remain under `.simtools/artifacts/`.

## Documentation Checks

- `README.md` quick start is current.
- `CHANGELOG.md` has the release entry.
- `docs/10_ROADMAP.md` reflects the next target.
- `docs/07_TOOL_MATRIX.md` and `docs/08_INSTALLATION_PROFILES.md` match
  manifests.

## GitHub Checks

- GitHub Actions test workflow passes.
- Branch is pushed to the intended remote.
- Release notes mention limitations and opt-in simulator behavior.

## Optional Real Simulator Checks

These are not CI defaults:

```bash
./scripts/validate_ai2thor.sh
```
