# Adapter Contract

Every simulator is represented by a YAML manifest and a lightweight Python
adapter. The adapter bridges SimTools commands to the simulator without forcing
the simulator into the base environment.

## Interface

```python
from abc import ABC, abstractmethod
from typing import Any

class SimToolAdapter(ABC):
    tool_id: str

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def check_installed(self) -> bool:
        ...

    @abstractmethod
    def doctor(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def smoke(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def launch_viewer(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def sample_commands(self) -> list[str]:
        ...
```

## Lazy Import Rules

- Adapter modules may import only lightweight stdlib and SimTools modules at
  module import time.
- Heavy simulator packages must be checked with `importlib.util.find_spec`.
- Heavy simulator packages may be imported only inside an explicit execution
  method such as `smoke(execute=True)` or an opt-in viewer launch.

## Smoke Test Rules

- If the simulator is not installed, return `status: skipped` with next steps.
- If installed, the smoke test must be minimal and non-destructive.
- Tests must not run real simulator smoke tests.
- Any artifact must be written under `.simtools/artifacts/<tool_id>/`.

## Installation Profile Rules

- Installation profiles live in manifests.
- `simtools install-plan <tool_id>` prints commands only.
- Future execution of install profiles must require an explicit `--execute`
  flag and should still avoid system package mutation unless requested.

## Error Handling Rules

- Return structured dictionaries from adapter methods.
- Include `status`, `message`, and `next_steps` where useful.
- Avoid hard crashes for missing packages, assets, GPU, or display servers.

## Add a New Simulator

Add a manifest, adapter, tests, docs matrix update, installation profile update,
and dry-run smoke command. Do not add simulator-specific branches to the CLI.
