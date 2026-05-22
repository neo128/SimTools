# AI2-THOR Validation

This document records the first isolated AI2-THOR validation path.

For day-to-day launch commands, viewer controls, artifact usage, and
troubleshooting, see `docs/14_QUICK_USE.md`.

## Environment

The base SimTools environment is not used for AI2-THOR. Validation uses a
repository-local isolated conda prefix:

```bash
conda create -p ./.venv-ai2thor python=3.11 pip -y
.venv-ai2thor/bin/python -m pip install -e . ai2thor
```

`.venv-ai2thor/` is ignored by git.

## Commands

```bash
.venv-ai2thor/bin/python -m simtools doctor ai2thor
.venv-ai2thor/bin/python -m simtools validate
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke --dry-run
.venv-ai2thor/bin/python -m simtools view ai2thor --execute --scene FloorPlan1 --width 300 --height 300 --max-actions 0
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke
.venv-ai2thor/bin/python -m simtools artifacts ai2thor
```

## Result

Validated on 2026-05-22:

- `doctor ai2thor`: installed
- `validate`: passed, 6 tools and 4 profiles
- dry-run smoke: planned
- viewer launch-and-close validation: passed
- real smoke: passed
- artifact screenshot: `.simtools/artifacts/ai2thor/smoke_20260522T092610Z.ppm`
- artifact report: `.simtools/artifacts/ai2thor/smoke_report_20260522T092611Z.json`

The screenshot was written as a PPM file to avoid adding image-writing
dependencies to SimTools.

## Notes

- This validation may download AI2-THOR runtime assets on first use.
- Do not run this in CI by default.
- Do not install AI2-THOR into the base SimTools environment.

## Interactive Viewer

Launch:

```bash
./scripts/view_ai2thor.sh FloorPlan1
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768
./scripts/view_ai2thor.sh FloorPlan1 --width 1024 --height 768 --max-actions 0
```

Controls:

- `w`: MoveAhead
- `s`: MoveBack
- `a`: RotateLeft
- `d`: RotateRight
- `u`: LookUp
- `j`: LookDown
- `shot`: save a PPM frame under `.simtools/artifacts/ai2thor/`
- `quit`: close the viewer

If the command appears idle, check the terminal for the `ai2thor>` prompt and
the desktop for the Unity window. The normal interactive path stays open until
`quit` or `Ctrl+C`.
