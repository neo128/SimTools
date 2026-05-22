# Quick Use

This document collects hands-on commands for launching, viewing, and interacting
with simulators through SimTools.

It starts with AI2-THOR because it is the first real integration path. Future
sections should use the same structure for Habitat, RoboCasa365, OmniGibson,
BEHAVIOR-1K, MolmoSpaces, and later tools.

## Rules

- Keep each simulator in its own isolated environment.
- Use SimTools as the launcher, registry, artifact, and documentation layer.
- Do not install real simulator packages into the base SimTools environment.
- GUI viewers are opt-in and must be started explicitly.
- Tests and CI must not launch real GUI viewers.

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
- `validate` reports 6 tools and 4 profiles

### Validate Viewer Launch

Use launch-and-close mode when you only want to confirm that Unity can start:

```bash
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768 --max-actions 0
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
2. Use the movement and camera buttons.
3. Select a visible object from the object panel.
4. Click object actions such as `Pick up`, `Open`, `Toggle on`, or
   `Put held object`.
5. Click `Save screenshot` to write a PPM artifact.
6. Click `Stop` when finished.

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

Status: planned quick-use section. The current Habitat adapter has an opt-in
import-only smoke path and does not launch a real viewer yet.

## RoboCasa365

Status: planned quick-use section. Keep RoboCasa365 in its own environment and
avoid downloading assets by default.

## OmniGibson

Status: planned quick-use section. Real viewer support will require explicit
Isaac Sim / Omniverse environment guidance.

## BEHAVIOR-1K

Status: planned quick-use section. Real usage depends on OmniGibson and large
assets, so it must remain opt-in.

## MolmoSpaces

Status: planned quick-use section. Real usage should document MuJoCo/runtime
requirements and asset handling.

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
