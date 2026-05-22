# Installation Profiles

Installation profiles are declarative command lists in tool manifests. SimTools
prints plans; it does not execute installers, download assets, accept licenses,
or mutate global environments by default.

## Profile Types

- `minimal`: smallest useful setup plan.
- `conda`: isolated conda or mamba environment plan.
- `source`: source checkout or editable install plan.
- `assets`: explicit asset download/setup plan.
- `headless`: explicit automated/headless setup plan.

## Show Plans

```bash
python -m simtools install-plan
python -m simtools install-plan ai2thor
python -m simtools install-plan maniskill
python -m simtools install-plan robocasa365 --profile assets
```

Every `install-plan` command is a dry-run printout.

## AI2-THOR

AI2-THOR is the first real adapter path:

```bash
python -m simtools install-plan ai2thor
python -m simtools doctor ai2thor
python -m simtools run ai2thor --mode smoke --dry-run
```

The real smoke is opt-in and runs only if `ai2thor` is already installed in the
active environment.

## Habitat

Habitat has an import-only preparation path:

```bash
python -m simtools install-plan habitat
python -m simtools doctor habitat
python -m simtools run habitat --mode smoke --dry-run
python -m simtools view habitat --dry-run
```

The current Habitat smoke checks package imports only. It does not launch
Habitat-Sim, open a GUI, or load dataset-backed scenes.

Source: <https://aihabitat.org/docs/habitat-lab/quickstart>

## ManiSkill

ManiSkill is the first planned expansion after AI2-THOR and Habitat:

```bash
python -m simtools install-plan maniskill
python -m simtools doctor maniskill
python -m simtools run maniskill --mode smoke --dry-run
python -m simtools view maniskill --dry-run
```

The non-dry-run smoke is package-only and lazy imports `mani_skill` if it is
already installed. Rendering and real viewer checks remain opt-in because they
can depend on Vulkan and GPU driver setup.

Source: <https://maniskill.readthedocs.io/en/v3.0.0b20/user_guide/getting_started/installation.html>

## RoboCasa365

RoboCasa365 is represented by a dry-run planned adapter:

```bash
python -m simtools install-plan robocasa365
python -m simtools install-plan robocasa365 --profile assets
python -m simtools doctor robocasa365
python -m simtools run robocasa365 --mode smoke --dry-run
python -m simtools view robocasa365 --dry-run
```

The `assets` profile is separate because official setup includes kitchen asset
downloads around 10GB. SimTools never starts that download automatically.

Source: <https://robocasa.ai/docs/build/html/introduction/installation.html>

## MolmoSpaces

MolmoSpaces is represented by a dry-run planned adapter:

```bash
python -m simtools install-plan molmospaces
python -m simtools install-plan molmospaces --profile conda
python -m simtools doctor molmospaces
python -m simtools run molmospaces --mode smoke --dry-run
python -m simtools view molmospaces --dry-run
```

Official debug/data-generation commands can auto-download assets, so SimTools
keeps them as manual viewer guidance until cache and artifact policies are
implemented.

Source: <https://github.com/allenai/molmospaces>

## OmniGibson

OmniGibson is represented by a dry-run planned adapter:

```bash
python -m simtools install-plan omnigibson
python -m simtools install-plan omnigibson --profile source
python -m simtools doctor omnigibson
python -m simtools run omnigibson --mode smoke --dry-run
python -m simtools view omnigibson --dry-run
```

Real execution depends on Isaac Sim / Omniverse, NVIDIA driver compatibility,
display or headless rendering mode, and asset locations.

Source: <https://behavior.stanford.edu/getting_started/installation.html>

## BEHAVIOR-1K

BEHAVIOR-1K is represented by a dry-run planned adapter:

```bash
python -m simtools install-plan behavior1k
python -m simtools install-plan behavior1k --profile source
python -m simtools doctor behavior1k
python -m simtools run behavior1k --mode smoke --dry-run
python -m simtools view behavior1k --dry-run
```

The default profile avoids dataset download flags. Dataset-backed setup must
remain explicit because it can accept licenses and download large assets.

Source: <https://behavior.stanford.edu/getting_started/installation.html>
