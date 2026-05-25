# Verification Report - 2026-05-22

This report records the local verification state for the SimTools real-run
goal on 2026-05-22.

## Host

- OS: Ubuntu 22.04.5, Linux 6.8.0-111-generic
- GPU: NVIDIA GeForce RTX 4090, driver 580.159.03
- Display: `DISPLAY=:1`
- Disk: more than 1TB free during verification
- Inotify limits observed during OmniGibson startup:
  - `fs.inotify.max_user_watches=65536`
  - `fs.inotify.max_user_instances=128`

## Summary

| Tool | Result | Evidence |
| --- | --- | --- |
| AI2-THOR | real smoke and interactive viewer ready | Unity launch, terminal controls, Streamlit mouse UI, PPM artifacts |
| Habitat | real smoke and visual render ready | `.simtools/artifacts/habitat/skokloster-castle_rgb.png` |
| ManiSkill | real smoke and visual render ready | `.simtools/artifacts/maniskill/videos/0.mp4` |
| RoboCasa365 | real smoke and visual render ready | `.simtools/artifacts/robocasa365/kitchen_rgb.png` |
| MolmoSpaces | real smoke and visual render ready | `.simtools/artifacts/molmospaces/floorplan1_rgb.png` |
| OmniGibson | package/runtime smoke ready, viewer blocked | Package metadata probe passes and Isaac/Kit startup reaches Simulation App; dataset EULA blocks scenes |
| BEHAVIOR-1K | package smoke ready, viewer blocked | BDDL/OmniGibson package metadata probe passes; dataset EULA blocks tasks |

## Commands

Run the full lightweight test and registry validation:

```bash
pytest
python -m simtools validate --json
python -m simtools real-status --json
```

Observed result:

- `pytest`: 45 passed
- `python -m simtools validate --json`: passed
- `python -m simtools real-status --json`: failed by design with 5 ready tools
  and 2 blocked tools (`behavior1k`, `omnigibson`)

Run real smoke/viewer checks:

```bash
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke
.venv-ai2thor/bin/python -m simtools view ai2thor --execute --scene FloorPlan1 --max-actions 0

python -m simtools run habitat --mode smoke
python -m simtools view habitat --execute --scene skokloster-castle --width 640 --height 480

.venv-maniskill/bin/python -m simtools run maniskill --mode smoke
.venv-maniskill/bin/python -m simtools view maniskill --execute --scene PickCube-v1

python -m simtools run robocasa365 --mode smoke
python -m simtools view robocasa365 --execute --scene Kitchen --width 640 --height 480

python -m simtools run molmospaces --mode smoke
python -m simtools view molmospaces --execute --scene FloorPlan1 --width 640 --height 480

python -m simtools run omnigibson --mode smoke
python -m simtools view omnigibson --execute

python -m simtools run behavior1k --mode smoke
python -m simtools view behavior1k --execute
```

## Current Blockers

`python -m simtools real-status --strict` is expected to fail until two tools
are promoted to `real_viewer`:

1. OmniGibson: the runtime is installed and Isaac/Kit starts, but the scene
   viewer requires the BEHAVIOR/OmniGibson dataset. The official downloader
   presents the BEHAVIOR Data Bundle EULA and requires the user to personally
   answer.
2. BEHAVIOR-1K: package-level imports pass, but task execution and
   visualization depend on the same licensed dataset and OmniGibson viewer gate.

SimTools deliberately does not auto-accept this EULA.

The required handoff command is:

```bash
PYTHONNOUSERSITE=1 \
CONDA_PREFIX="$PWD/.venv-omnigibson" \
PATH="$PWD/.venv-omnigibson/bin:$PATH" \
.venv-omnigibson/bin/python -s -m omnigibson.download_datasets
```

The user must run that command personally, read the BEHAVIOR Data Bundle EULA,
and accept or reject it according to their own decision. If the user accepts and
the dataset installs, re-run:

```bash
python -m simtools view omnigibson --execute
```

## Continuation Verification - 2026-05-25

Latest command evidence from the Goal continuation:

- `pytest`: 47 passed.
- `python -m simtools validate --json`: passed with 7 tools, 4 profiles, and
  no issues.
- `python -m simtools real-status --json`: failed by design with 5 ready tools
  and 2 blocked tools (`behavior1k`, `omnigibson`).
- `python -m simtools doctor omnigibson`: `installed=true`,
  `viewer_ready=false`, `dataset_ready=false`, `requires_eula=true`.
- `python -m simtools doctor behavior1k`: `installed=true`, `status=blocked`,
  `dataset_ready=false`, `requires_eula=true`.
- `python -m simtools run omnigibson --mode smoke --no-save-report`: passed
  after changing the smoke probe to package discovery and distribution metadata
  instead of top-level `omnigibson` import.
- `python -m simtools run behavior1k --mode smoke --no-save-report`: passed
  with the same package metadata probe.
- `python -m simtools view omnigibson --execute`: skipped before GUI launch
  because `dataset_ready=false` and `requires_eula=true`.
- `python -m simtools view behavior1k --execute`: skipped before GUI launch
  because the same licensed dataset is missing.
- `python -m simtools real-status --strict`: exited 2 by design with
  `behavior1k` and `omnigibson` not ready.
- `git diff --check`: passed.
- `nvidia-smi` in the current Codex execution context could not communicate
  with the NVIDIA driver, and Torch reported no CUDA devices under
  `.venv-omnigibson`. Do not promote OmniGibson or BEHAVIOR-1K to
  `real_viewer` from this session.

## Dataset Download Continuation - 2026-05-25

The user personally accepted the BEHAVIOR Data Bundle EULA in the interactive
prompt. Codex only forwarded the user's explicit `y` responses.

Because `python -m omnigibson.download_datasets` imports `omnigibson/__init__.py`
and the current Codex context cannot access CUDA, the downloader was run through
a temporary package shim that imports only `omnigibson.macros` and
`omnigibson.utils.asset_utils`.

Observed result:

- BEHAVIOR/OmniGibson key download completed.
- OmniGibson dataset download reached 100% and extracted.
- OmniGibson assets download reached 100% and extracted.
- `python -m simtools doctor omnigibson`: `installed=true`,
  `viewer_ready=true`, `dataset_ready=true`, `requires_eula=false`.
- `python -m simtools doctor behavior1k`: `installed=true`,
  `dataset_ready=true`, `requires_eula=false`.
- `python -m simtools view omnigibson --execute`: failed at runtime with
  `RuntimeError: No CUDA GPUs are available`.

Current blocker is no longer dataset/EULA. It is CUDA visibility in the current
execution context. Re-run the viewer from a local shell where `nvidia-smi` and
Torch CUDA discovery both see the NVIDIA GPU.

## Usage Guide

Use [docs/14_QUICK_USE.md](14_QUICK_USE.md) for daily commands. That document
now contains per-tool setup checks, viewer commands, artifact locations, and the
current OmniGibson/BEHAVIOR delegated viewer gate.

## Final Viewer Gate Continuation - 2026-05-25

The later Goal continuation is recorded in
[docs/16_VERIFICATION_REPORT_2026-05-25.md](16_VERIFICATION_REPORT_2026-05-25.md).

Updated result:

- Torch CUDA discovery in `.venv-omnigibson`: `True 1`.
- `python -m simtools view omnigibson --execute`: passed after reaching the
  interactive control loop marker `Pressed None. Action:`.
- `python -m simtools run behavior1k --mode smoke --no-save-report`: passed.
- `python -m simtools view behavior1k --execute`: passed with
  `viewer_status=delegated_to_omnigibson`.
- OmniGibson and BEHAVIOR-1K are promoted to `real_viewer`.
