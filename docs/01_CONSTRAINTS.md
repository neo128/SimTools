# Constraints

These constraints are part of the architecture, not suggestions.

1. Do not install all simulators into the same Python environment.
2. Do not load heavyweight simulators during module import.
3. Do not download large files or launch real GUIs during tests.
4. Do not run `sudo`, `apt`, `brew`, `conda install`, or equivalent mutating
   package-manager commands by default.
5. Do not modify a user's shell profile automatically.
6. Do not download BEHAVIOR, MolmoSpaces, RoboCasa, or other large assets by
   default.
7. Expose real installation actions only through explicit install profiles.
8. Add every tool through an adapter + manifest pair.
9. Provide dry-run behavior for commands that would start processes, launch
   viewers, run smoke tests, or install dependencies.
10. Failures must include practical next steps for the user.

## Base Environment

The base SimTools environment may include lightweight libraries such as Typer,
Rich, Pydantic, PyYAML, pytest, and optionally Streamlit. It must not include
AI2-THOR, Habitat, OmniGibson, BEHAVIOR-1K, MolmoSpaces, RoboCasa365, MuJoCo, or
Isaac Sim as required dependencies.

## Testing Boundary

Unit tests validate manifests, registry behavior, capability matrices, adapter
contracts, and command output. They do not require a GPU, simulator runtime,
dataset, Unity process, Isaac Sim process, MuJoCo license, or GUI session.
