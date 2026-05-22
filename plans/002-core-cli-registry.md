# Plan 002: Core CLI Registry

## Goal

Build the lightweight Python scaffold: config models, manifest loader, registry,
capability matrix, and CLI commands.

## Steps

1. Add `pyproject.toml`.
2. Add package files under `src/simtools/`.
3. Add global config, profiles, and tool manifests.
4. Implement list, info, compare, and doctor.
5. Add tests for loader, registry, and matrix generation.

## Constraints

- No real simulator installation.
- No eager imports of simulator packages.
- No GUI launch.
