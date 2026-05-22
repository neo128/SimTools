# Quick Use

This document collects hands-on commands for launching, viewing, and interacting
with simulators through SimTools.

It starts with AI2-THOR because it is the first real integration path. Other
sections use the same structure for Habitat, ManiSkill, RoboCasa365,
MolmoSpaces, OmniGibson, BEHAVIOR-1K, and later tools.

## Rules

- Keep each simulator in its own isolated environment.
- Use SimTools as the launcher, registry, artifact, and documentation layer.
- Do not install real simulator packages into the base SimTools environment.
- GUI viewers are opt-in and must be started explicitly.
- Tests and CI must not launch real GUI viewers.
- A tool is not fully integrated until `python -m simtools real-status` reports
  `stage=real_viewer`, local run is `yes`, smoke is `yes`, and visual is `yes`.

Check the current truth:

```bash
python -m simtools real-status
python -m simtools real-status --strict
```

The strict command is expected to fail until every registered tool has a real
local smoke and visualization proof. See
`docs/15_REAL_LOCAL_RUN_REQUIREMENTS.md`.

## AI2-THOR

AI2-THOR uses an isolated repository-local Python environment:

```bash
conda create -p ./.venv-ai2thor python=3.11 pip -y
.venv-ai2thor/bin/python -m pip install -e . ai2thor
```

The `.venv-ai2thor/` directory is ignored by git.

### Check Setup

```bash
.venv-ai2thor/bin/python -m simtools doctor ai2thor
.venv-ai2thor/bin/python -m simtools validate
```

Expected result:

- `doctor ai2thor` reports `installed`
- `validate` reports 7 tools and 4 profiles

### Scenes

SimTools currently targets AI2-THOR's public iTHOR scene set. iTHOR has 120
scenes, evenly split across four room types. The public AI2-THOR scene names are
case-sensitive and follow this pattern:

| Room type | Count | Scene names |
| --- | ---: | --- |
| Kitchen | 30 | `FloorPlan1` ... `FloorPlan30` |
| Living room | 30 | `FloorPlan201` ... `FloorPlan230` |
| Bedroom | 30 | `FloorPlan301` ... `FloorPlan330` |
| Bathroom | 30 | `FloorPlan401` ... `FloorPlan430` |

For machine learning experiments, the common split is first 20 scenes for
training, next 5 for validation, and last 5 for testing within each room type.
For example, kitchens usually split as:

| Split | Kitchen example |
| --- | --- |
| train | `FloorPlan1` ... `FloorPlan20` |
| validation | `FloorPlan21` ... `FloorPlan25` |
| test | `FloorPlan26` ... `FloorPlan30` |

The same split pattern applies to living rooms, bedrooms, and bathrooms.

AI2-THOR's Python package may internally normalize public scene names such as
`FloorPlan1` to physics scene names such as `FloorPlan1_physics`; in SimTools
commands, use the public names like `FloorPlan1`.

Source: <https://ai2thor.allenai.org/ithor/documentation/scenes/>

### Switch Scene

All AI2-THOR launchers use the scene name. For terminal viewer, close the
current viewer with `quit`, then relaunch with another scene:

```bash
./scripts/view_ai2thor.sh FloorPlan201
```

For direct CLI usage, pass `--scene`:

```bash
.venv-ai2thor/bin/python -m simtools view ai2thor --execute --scene FloorPlan301
```

For the mouse UI, use the `iTHOR scene` dropdown in the sidebar and click
`Start / Reset` to load the selected scene.

### Validate Viewer Launch

Use launch-and-close mode when you only want to confirm that Unity can start:

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768 --max-actions 0
```

Replace `FloorPlan1` with any scene name:

```bash
./scripts/view_ai2thor.sh FloorPlan201 --width 1024 --height 768 --max-actions 0
./scripts/view_ai2thor.sh FloorPlan301 --width 1024 --height 768 --max-actions 0
./scripts/view_ai2thor.sh FloorPlan401 --width 1024 --height 768 --max-actions 0
```

Expected output:

```json
{
  "tool_id": "ai2thor",
  "status": "passed",
  "message": "AI2-THOR Unity viewer launched and closed.",
  "scene": "FloorPlan1",
  "actions_run": 0
}
```

### Start Interactive Viewer

Terminal-controlled Unity viewer:

```bash
./scripts/view_ai2thor.sh FloorPlan1
./scripts/view_ai2thor.sh FloorPlan201
```

With a specific window size:

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768
```

Equivalent direct command:

```bash
.venv-ai2thor/bin/python -m simtools view ai2thor --execute --scene FloorPlan1 --width 1024 --height 768
```

The terminal prints startup progress, then shows:

```text
AI2-THOR Unity viewer is ready.
ai2thor>
```

At that point the Unity window should be open and the terminal is waiting for
control commands.

### Start Mouse UI

Use the mouse-driven Streamlit UI when you want on-page buttons instead of
typing terminal commands. Install Streamlit in the isolated AI2-THOR environment
first if it is not already present:

```bash
.venv-ai2thor/bin/python -m pip install streamlit
```

Launch:

```bash
./scripts/view_ai2thor_ui.sh FloorPlan1 --width 1024 --height 768 --port 8502
```

You can also start directly in another scene:

```bash
./scripts/view_ai2thor_ui.sh FloorPlan201 --width 1024 --height 768 --port 8502
```

Equivalent direct command:

```bash
.venv-ai2thor/bin/python -m simtools view ai2thor --ui --execute --scene FloorPlan1 --width 1024 --height 768 --port 8502
```

Open the URL printed by Streamlit, usually:

```text
http://localhost:8502
```

In the page:

1. Click `Start / Reset`.
2. Use the `iTHOR scene` dropdown in the sidebar to choose another scene.
3. Click `Start / Reset` again to switch scenes.
4. Use the movement and camera buttons.
5. Select a visible object from the object panel.
6. Click object actions such as `Pick up`, `Open`, `Toggle on`, or
   `Put held object`.
7. Click `Save screenshot` to write a PPM artifact.
8. Click `Stop` when finished.

### Controls

Terminal controls:

| Command | Action |
| --- | --- |
| `w` | MoveAhead |
| `s` | MoveBack |
| `a` | RotateLeft |
| `d` | RotateRight |
| `u` | LookUp |
| `j` | LookDown |
| `shot` | Save the current RGB frame as a PPM artifact |
| `help` | Print controls |
| `quit` | Close the viewer |

You can also type a raw AI2-THOR action name such as `RotateRight`.

Mouse UI controls:

| UI Control | Action |
| --- | --- |
| `Forward` | MoveAhead |
| `Back` | MoveBack |
| `Left` | RotateLeft |
| `Right` | RotateRight |
| `Look up` | LookUp |
| `Look down` | LookDown |
| Visible object select box | Choose an object from AI2-THOR metadata |
| `Pick up` | PickupObject |
| `Open` / `Close` | OpenObject / CloseObject |
| `Toggle on` / `Toggle off` | ToggleObjectOn / ToggleObjectOff |
| `Put held object` | PutObject |
| `Save screenshot` | Save the current RGB frame as a PPM artifact |

### Artifacts

Screenshots and reports are written under:

```text
.simtools/artifacts/ai2thor/
```

List AI2-THOR artifacts:

```bash
python -m simtools artifacts ai2thor
```

Interactive screenshots created with `shot` are named like:

```text
viewer_YYYYMMDDTHHMMSSZ.ppm
```

Mouse UI screenshots are named like:

```text
viewer_ui_YYYYMMDDTHHMMSSZ.ppm
```

Smoke screenshots are named like:

```text
smoke_YYYYMMDDTHHMMSSZ.ppm
```

### Smoke Test

Dry-run plan:

```bash
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke --dry-run
```

Real opt-in smoke:

```bash
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke
```

The real smoke launches `FloorPlan1`, performs one `MoveAhead`, and writes a PPM
screenshot plus a JSON report under `.simtools/artifacts/ai2thor/`.

### Troubleshooting

If the command appears to hang:

- Check whether the Unity window is already open.
- Check whether the terminal is waiting at `ai2thor>`.
- Type `help` to print controls.
- Type `quit` or press `Ctrl+C` to close the interactive session.
- Run `--max-actions 0` to validate startup without entering interactive mode.

If the command never reaches `AI2-THOR Unity viewer is ready`:

- First launch may download or initialize the AI2-THOR Unity runtime.
- Confirm that your display is available, for example `echo "$DISPLAY"`.
- Confirm that the isolated environment exists:

```bash
ls .venv-ai2thor/bin/python
```

To inspect running AI2-THOR processes:

```bash
ps -ef | rg "(simtools view ai2thor|thor-Linux64|view_ai2thor.sh)"
```

If the mouse UI does not start:

- Confirm Streamlit is installed in `.venv-ai2thor`.
- Run a dry-run plan first:

```bash
.venv-ai2thor/bin/python -m simtools view ai2thor --ui --dry-run --scene FloorPlan1
```

- Start the UI on a different port if `8502` is already in use:

```bash
./scripts/view_ai2thor_ui.sh FloorPlan1 --port 8503
```

## Habitat

Status: package-level preparation path. The current Habitat adapter can check
imports and print viewer guidance, but it does not launch Habitat-Sim yet.

### Check Setup

```bash
python -m simtools install-plan habitat
python -m simtools doctor habitat
python -m simtools run habitat --mode smoke --dry-run
```

If Habitat and Habitat-Sim are installed in the active isolated environment, a
non-dry-run smoke lazy imports those packages only:

```bash
python -m simtools run habitat --mode smoke
```

### Viewer Plan

```bash
python -m simtools view habitat --dry-run
```

Use official Habitat examples manually until SimTools gets a dedicated opt-in
viewer. Dataset-backed scenes must be downloaded outside base tests.

Source: <https://aihabitat.org/docs/habitat-lab/quickstart>

## ManiSkill

Status: package-level preparation path. ManiSkill is useful as the next real
viewer candidate because it is lighter than Isaac/Omniverse stacks but still
gives manipulation tasks.

### Check Setup

```bash
python -m simtools install-plan maniskill
python -m simtools doctor maniskill
python -m simtools run maniskill --mode smoke --dry-run
```

If ManiSkill is installed in the active isolated environment, a non-dry-run
smoke lazy imports `mani_skill` only:

```bash
python -m simtools run maniskill --mode smoke
```

### Viewer Plan

```bash
python -m simtools view maniskill --dry-run
```

Manual official validation command after installation:

```bash
python -m mani_skill.examples.demo_random_action -e PickCube-v1
```

Rendering may require Vulkan and compatible GPU drivers. Keep rendered viewer
tests opt-in and outside base pytest.

Source: <https://maniskill.readthedocs.io/en/v3.0.0b20/user_guide/getting_started/installation.html>

## RoboCasa365

Status: dry-run planning. Keep RoboCasa365 in its own environment and avoid
downloading kitchen assets by default.

### Check Setup

```bash
python -m simtools install-plan robocasa365
python -m simtools doctor robocasa365
python -m simtools run robocasa365 --mode smoke --dry-run
```

### Asset Plan

```bash
python -m simtools install-plan robocasa365 --profile assets
```

This profile is separated because official docs note kitchen assets are around
10GB. SimTools only prints the plan.

### Viewer Plan

```bash
python -m simtools view robocasa365 --dry-run
```

Source: <https://robocasa.ai/docs/build/html/introduction/installation.html>

## MolmoSpaces

Status: dry-run planning. MolmoSpaces can use MuJoCo and provides assets usable
across MuJoCo, Isaac, and ManiSkill, but official debug commands can trigger
asset downloads.

### Check Setup

```bash
python -m simtools install-plan molmospaces
python -m simtools install-plan molmospaces --profile conda
python -m simtools doctor molmospaces
python -m simtools run molmospaces --mode smoke --dry-run
```

### Viewer Plan

```bash
python -m simtools view molmospaces --dry-run
```

Manual official debug viewer commands after installation:

```bash
python scripts/datagen/run_pipeline.py --viewer --seed 3
mjpython scripts/datagen/run_pipeline.py --viewer --seed 3
```

Set asset/cache locations before running commands that can download assets.

Source: <https://github.com/allenai/molmospaces>

## OmniGibson

Status: dry-run planning. Real viewer support requires explicit Isaac Sim /
Omniverse environment guidance.

### Check Setup

```bash
python -m simtools install-plan omnigibson
python -m simtools install-plan omnigibson --profile source
python -m simtools doctor omnigibson
python -m simtools run omnigibson --mode smoke --dry-run
```

### Viewer Plan

```bash
python -m simtools view omnigibson --dry-run
```

Manual official examples after installation:

```bash
python -m omnigibson.examples.robots.robot_control_example --quickstart
python -m omnigibson.examples.scenes.scene_selector
```

Confirm NVIDIA driver, Isaac Sim, display/headless mode, and asset locations
before executing.

Source: <https://behavior.stanford.edu/getting_started/installation.html>

## BEHAVIOR-1K

Status: dry-run planning. Real usage depends on OmniGibson and large assets, so
it must remain opt-in.

### Check Setup

```bash
python -m simtools install-plan behavior1k
python -m simtools install-plan behavior1k --profile source
python -m simtools doctor behavior1k
python -m simtools run behavior1k --mode smoke --dry-run
```

### Viewer Plan

```bash
python -m simtools view behavior1k --dry-run
```

Dataset-backed setup must remain explicit because it can accept licenses,
download Isaac Sim, and download BEHAVIOR datasets.

Source: <https://behavior.stanford.edu/getting_started/installation.html>

## New Tool Section Template

Use this structure when adding another simulator:

```markdown
## <Tool Name>

### Check Setup

### Validate Viewer Launch

### Start Interactive Viewer

### Controls

### Artifacts

### Smoke Test

### Troubleshooting
```
