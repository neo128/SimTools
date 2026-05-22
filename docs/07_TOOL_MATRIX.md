# Tool Matrix

| ID | Tool | Backend | Install Level | Visualization | Headless | GPU | Large Assets |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ai2thor | AI2-THOR | Unity | light | yes | yes | optional | no |
| habitat | Habitat | Habitat-Sim | medium | yes | yes | recommended | optional |
| maniskill | ManiSkill | SAPIEN / PhysX | medium | yes | yes | optional | optional |
| behavior1k | BEHAVIOR-1K | OmniGibson | heavy | via OmniGibson | partial | recommended | yes |
| omnigibson | OmniGibson | Isaac Sim / NVIDIA Omniverse | heavy | yes | partial | recommended | yes |
| molmospaces | MolmoSpaces | MuJoCo | medium | yes | yes | optional | yes |
| robocasa365 | RoboCasa365 | MuJoCo | medium | yes | yes | optional | yes |

This matrix is generated from manifests by the CLI and should be kept aligned
with `configs/tools/*.yaml`.
