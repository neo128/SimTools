# Installation Profiles

Installation profiles are declarative command lists in tool manifests. SimTools
prints plans; it does not execute them by default.

## Profiles

- `minimal`: smallest useful Python-level setup.
- `conda`: isolated conda or mamba environment plan.
- `docker`: future container-oriented setup plan.
- `source`: future source checkout plan.

## Current First-Class Path

AI2-THOR is the first real adapter target because it is comparatively light:

```bash
simtools install-plan ai2thor
```

This prints:

```bash
pip install ai2thor
```

It does not execute the command automatically.

## Heavy Tools

BEHAVIOR-1K, OmniGibson, MolmoSpaces, and RoboCasa365 often need large assets,
external runtimes, or GPU/display setup. Their profiles are documentation-grade
until a dedicated opt-in adapter path is added.
