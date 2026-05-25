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

Habitat now has a real local visual path through `.venv-habitat`:

```bash
python -m simtools install-plan habitat
python -m simtools install-plan habitat --profile conda
python -m simtools install-plan habitat --profile assets
python -m simtools doctor habitat
python -m simtools run habitat --mode smoke --dry-run
python -m simtools view habitat --dry-run
```

The verified profile uses the official conda `habitat-sim` package plus
`habitat-lab` in `.venv-habitat`. Because that package path uses Python 3.9,
the base SimTools CLI launches it as an external profile.

After the test scenes are present, render one RGB artifact:

```bash
python -m simtools run habitat --mode smoke
python -m simtools view habitat --execute --scene skokloster-castle --width 640 --height 480
```

The viewer command writes:

```text
.simtools/artifacts/habitat/skokloster-castle_rgb.png
```

Base pytest still does not render Habitat frames; the visual path is opt-in.

Source: <https://aihabitat.org/docs/habitat-lab/quickstart>

## ManiSkill

ManiSkill now has a real local visual path:

```bash
python -m simtools install-plan maniskill
python -m simtools doctor maniskill
python -m simtools run maniskill --mode smoke --dry-run
python -m simtools view maniskill --dry-run
```

The non-dry-run smoke lazy imports `mani_skill`. The opt-in viewer path renders
a short `PickCube-v1` MP4 artifact through the official `demo_random_action`
script:

```bash
.venv-maniskill/bin/python -m simtools view maniskill --execute --scene PickCube-v1
```

Rendering still stays outside base pytest because it depends on Vulkan and GPU
driver setup.

Source: <https://maniskill.readthedocs.io/en/v3.0.0b20/user_guide/getting_started/installation.html>

## RoboCasa365

RoboCasa365 now has a real local visual path through `.venv-robocasa365`:

```bash
python -m simtools install-plan robocasa365
python -m simtools install-plan robocasa365 --profile assets
python -m simtools doctor robocasa365
python -m simtools run robocasa365 --mode smoke --dry-run
python -m simtools view robocasa365 --dry-run
```

The verified setup uses editable checkouts of `robosuite` and `robocasa`.
Kitchen assets were downloaded explicitly with the official script before
running the real visual path.

```bash
python -m simtools run robocasa365 --mode smoke
python -m simtools view robocasa365 --execute --scene Kitchen --width 640 --height 480
```

The viewer command writes:

```text
.simtools/artifacts/robocasa365/kitchen_rgb.png
```

Source: <https://robocasa.ai/docs/build/html/introduction/installation.html>

## MolmoSpaces

MolmoSpaces now has a real local visual path through `.venv-molmospaces`:

```bash
python -m simtools install-plan molmospaces
python -m simtools install-plan molmospaces --profile conda
python -m simtools doctor molmospaces
python -m simtools run molmospaces --mode smoke --dry-run
python -m simtools view molmospaces --dry-run
```

The verified setup uses the source checkout plus one explicit iTHOR scene asset
fetch into repository-local cache and asset directories:

```bash
MLSPACES_CACHE_DIR="$PWD/.simtools/molmospaces-cache" \
MLSPACES_ASSETS_DIR="$PWD/.simtools/molmospaces-assets" \
MLSPACES_FORCE_INSTALL=True \
.venv-molmospaces/bin/python .simtools/external/molmospaces/scripts/datagen/fetch_assets.py scene ithor 1 --split train
```

Run:

```bash
python -m simtools run molmospaces --mode smoke
python -m simtools view molmospaces --execute --scene FloorPlan1 --width 640 --height 480
```

The viewer command writes:

```text
.simtools/artifacts/molmospaces/floorplan1_rgb.png
```

Source: <https://github.com/allenai/molmospaces>

## OmniGibson

OmniGibson is package/runtime and viewer verified through `.venv-omnigibson`:

```bash
python -m simtools install-plan omnigibson
python -m simtools install-plan omnigibson --profile source
python -m simtools doctor omnigibson
python -m simtools run omnigibson --mode smoke
python -m simtools view omnigibson --execute
```

Verified locally:

- `.venv-omnigibson` uses Python 3.10.
- `omnigibson==1.1.1`, `bddl==3.5.0`, and Isaac Sim `4.1.0.0` import.
- Torch CUDA discovery reports one local GPU.
- The BEHAVIOR/OmniGibson dataset and assets are installed after user EULA
  acceptance.
- The viewer reaches the interactive control loop and prints
  `Pressed None. Action:` before the SimTools verification timeout stops it.

Operational notes:

- The host reports `fs.inotify.max_user_watches=65536`, which produces Isaac
  `errno=28` watch warnings during extension startup.
- SimTools does not change host-level inotify/sysctl values.
- SimTools does not auto-accept the BEHAVIOR Data Bundle EULA.

Source: <https://behavior.stanford.edu/getting_started/installation.html>

## BEHAVIOR-1K

BEHAVIOR-1K has package-level smoke verified through the OmniGibson environment,
with visualization delegated to the verified OmniGibson viewer gate:

```bash
python -m simtools install-plan behavior1k
python -m simtools install-plan behavior1k --profile source
python -m simtools doctor behavior1k
python -m simtools run behavior1k --mode smoke
python -m simtools view behavior1k --execute
```

Verified locally:

- `bddl`, `omnigibson`, and `isaacsim` package probes pass in
  `.venv-omnigibson`.
- Dataset/assets are present after user EULA acceptance.
- `python -m simtools view behavior1k --execute` returns
  `viewer_status=delegated_to_omnigibson`.

SimTools will not auto-accept the BEHAVIOR Data Bundle EULA. Fresh machines
must run the official dataset command manually and deliberately before these
viewer gates can pass.

Source: <https://behavior.stanford.edu/getting_started/installation.html>
