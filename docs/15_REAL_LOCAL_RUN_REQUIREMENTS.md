# Real Local Run Requirements

The project goal is now stricter than metadata registration:

```text
Every fully integrated simulator must run locally and provide a verified
visualization path.
```

SimTools must not pretend that dry-run plans satisfy this goal. The registry can
include planned tools, but a tool is fully integrated only when its manifest
readiness stage is `real_viewer`.

## Gate

Run:

```bash
python -m simtools real-status
python -m simtools real-status --strict
```

`real-status --strict` exits non-zero until every registered tool has:

1. a dedicated local environment or explicit local runtime path
2. a non-dry-run smoke command
3. a real visualization command
4. a recorded verification date
5. artifacts or screenshots when practical
6. no unresolved readiness blockers

## Current Truth

| Tool | Stage | Real local run | Visualization verified | Meaning |
| --- | --- | --- | --- | --- |
| AI2-THOR | `real_viewer` | yes | yes | Terminal Unity viewer and mouse UI are wired. |
| Habitat | `real_viewer` | yes | yes | Habitat-Sim renders an RGB PNG from official test scenes. |
| ManiSkill | `real_viewer` | yes | yes | PickCube-v1 smoke and MP4 visual rendering are wired. |
| RoboCasa365 | `real_viewer` | yes | yes | MuJoCo EGL renders a Kitchen RGB PNG after official kitchen assets are present. |
| MolmoSpaces | `real_viewer` | yes | yes | MuJoCo EGL renders an iTHOR FloorPlan1 RGB PNG from fetched MolmoSpaces assets. |
| OmniGibson | `real_viewer` | yes | yes | OmniGibson, Isaac Sim, omni, BDDL, dataset/assets, CUDA discovery, and the interactive viewer gate are verified. |
| BEHAVIOR-1K | `real_viewer` | yes | yes | BDDL/OmniGibson package metadata smoke passes; dataset/assets are installed; visualization is delegated to the verified OmniGibson viewer gate. |

## Promotion Checklist

To promote a tool to `real_viewer`:

1. Create an isolated environment for that simulator.
2. Install only that simulator and its direct requirements there.
3. Run `python -m simtools doctor <tool_id>` in that environment.
4. Run `python -m simtools run <tool_id> --mode smoke`.
5. Run `python -m simtools view <tool_id> --execute` or the tool-specific
   viewer script.
6. Capture at least one screenshot, report, or launch-and-close proof under
   `.simtools/artifacts/<tool_id>/` when possible.
7. Update `configs/tools/<tool_id>.yaml` readiness fields.
8. Update `docs/14_QUICK_USE.md`.
9. Run `pytest`, `python -m simtools validate`, and
   `python -m simtools real-status`.

## Why Not Auto-Install Everything

Several tools require large assets, external runtimes, GPU/display setup, or
license acceptance:

- RoboCasa asset setup can download around 10GB of kitchen assets.
- MolmoSpaces scene setup can download a large cache before symlinking the
  selected scenes/assets into the active asset directory.
- OmniGibson and BEHAVIOR-1K depend on Isaac Sim / Omniverse and NVIDIA driver
  compatibility.
- BEHAVIOR/OmniGibson dataset setup requires explicit license acceptance and
  must be completed by the user, not by SimTools automation.

Therefore SimTools exposes plans and gates first. Real installation and viewer
execution must be deliberate, tool-by-tool, and recorded in readiness metadata.

Sources:

- AI2-THOR scenes: <https://ai2thor.allenai.org/ithor/documentation/scenes/>
- Habitat quickstart: <https://aihabitat.org/docs/habitat-lab/quickstart>
- ManiSkill install: <https://maniskill.readthedocs.io/en/v3.0.0b20/user_guide/getting_started/installation.html>
- RoboCasa install: <https://robocasa.ai/docs/build/html/introduction/installation.html>
- MolmoSpaces repo: <https://github.com/allenai/molmospaces>
- BEHAVIOR install: <https://behavior.stanford.edu/getting_started/installation.html>
