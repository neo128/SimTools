# Verification Report - 2026-05-25

This report records the Goal continuation that promoted OmniGibson and
BEHAVIOR-1K to `real_viewer`.

## Host

- OS: Ubuntu 22.04.5, Linux 6.8.0-111-generic
- GPU: NVIDIA GeForce RTX 4090, driver 580.159.03
- Torch CUDA check in `.venv-omnigibson`: `True 1`
- Display: local desktop session
- BEHAVIOR/OmniGibson dataset: present under
  `.venv-omnigibson/lib/python3.10/site-packages/omnigibson/data`

## Summary

| Tool | Result | Evidence |
| --- | --- | --- |
| AI2-THOR | real smoke and interactive viewer ready | Unity launch, terminal controls, Streamlit mouse UI, PPM artifacts |
| Habitat | real smoke and visual render ready | `.simtools/artifacts/habitat/skokloster-castle_rgb.png` |
| ManiSkill | real smoke and visual render ready | `.simtools/artifacts/maniskill/videos/0.mp4` |
| RoboCasa365 | real smoke and visual render ready | `.simtools/artifacts/robocasa365/kitchen_rgb.png` |
| MolmoSpaces | real smoke and visual render ready | `.simtools/artifacts/molmospaces/floorplan1_rgb.png` |
| OmniGibson | real smoke and interactive viewer ready | `python -m simtools view omnigibson --execute` reached `Pressed None. Action:` and timed out by design after 300 seconds |
| BEHAVIOR-1K | real smoke and delegated viewer ready | `python -m simtools view behavior1k --execute` returned `viewer_status=delegated_to_omnigibson` |

## Commands Observed

```bash
git status --short
python -m simtools validate --json
python -m simtools real-status --json
python -m simtools doctor omnigibson
python -m simtools doctor behavior1k
.venv-omnigibson/bin/python -s -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
python -m simtools run omnigibson --mode smoke --no-save-report
python -m simtools view omnigibson --execute
python -m simtools run behavior1k --mode smoke --no-save-report
python -m simtools view behavior1k --execute
```

Key results:

- `validate --json`: passed with 7 tools, 4 profiles, and no issues before
  readiness promotion.
- `real-status --json`: initially failed with 5 ready tools and 2 stale
  blockers (`behavior1k`, `omnigibson`).
- `doctor omnigibson`: `installed=true`, `viewer_ready=true`,
  `dataset_ready=true`, `requires_eula=false`.
- `doctor behavior1k`: `installed=true`, `dataset_ready=true`,
  `requires_eula=false`.
- Torch CUDA check: `True 1`.
- `run omnigibson --mode smoke --no-save-report`: `status=passed` with
  `omnigibson 1.1.1`, `isaacsim 4.1.0.0`, `bddl 3.5.0`, and dataset ready.
- `view omnigibson --execute`: `status=passed`, `timed_out=true`, and
  readiness marker `Pressed None. Action:` was present in stdout.
- `run behavior1k --mode smoke --no-save-report`: `status=passed`,
  `viewer_status=delegated_to_omnigibson`.
- `view behavior1k --execute`: `status=passed`,
  `viewer_status=delegated_to_omnigibson`.

## Artifact Proof

OmniGibson did not write a screenshot during the viewer gate. The evidence is a
launch proof report:

```text
.simtools/artifacts/omnigibson/viewer_launch_proof_20260525.json
```

This records the command, timeout behavior, CUDA discovery, and observed
readiness marker. The timeout is expected because the official quickstart viewer
enters an interactive control loop.

## Final Gate

After updating readiness metadata, these final checks passed:

```bash
pytest
python -m compileall -q src simtools tests
python -m simtools validate --json
python -m simtools real-status --json
python -m simtools real-status --strict
python -m simtools list
python -m simtools compare
git diff --check
```

Observed result:

- `pytest`: 49 passed.
- `compileall`: passed.
- `validate --json`: passed with 7 tools, 4 profiles, and no issues.
- `real-status --json`: passed with `ready_count=7` and `not_ready_count=0`.
- `real-status --strict`: passed with `Real-ready tools: 7/7`.
- `list` and `compare`: rendered successfully.
- `git diff --check`: passed.

## Safety Notes

- No `sudo` commands were run.
- No system-level sysctl values were changed.
- No EULA was accepted by automation.
- Real viewer execution remains opt-in.
- Pytest must not start OmniGibson, Isaac Sim, or any real GUI.
- Base tests continue to avoid importing heavy simulator modules at import time.
