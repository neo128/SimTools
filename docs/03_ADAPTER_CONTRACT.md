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

## Viewer Rules

- Viewer launch must be dry-run by default.
- Real viewer execution must require an explicit `--execute` path.
- Tests must never launch a GUI viewer.
- Viewer adapters may accept options such as `scene`, `width`, `height`, and
  `max_actions`.
- Automation can use `--max-actions 0` to validate launch-and-close behavior
  without entering an interactive loop.

## Smoke Test Rules

- If the simulator is not installed, return `status: skipped` with next steps.
- If installed, the smoke test must be minimal and non-destructive.
- Tests must not run real simulator smoke tests.
- Any artifact must be written under `.simtools/artifacts/<tool_id>/`.

## Experiment Rules

- Experiment dry-runs must be satisfied by metadata and manifest commands, not
  by real adapter execution.
- Workbench v0.2 may route non-dry-run experiments to existing adapter methods:
  AI2-THOR `smoke`, Habitat `launch_viewer`, and ManiSkill `launch_viewer`.
- Adapter results should include `artifact` or `artifacts` paths when a real run
  creates visual output, so the run report can record artifact references.
- Adapter results may include `stdout` and `stderr` strings. Workbench v0.3
  writes these to `stdout.log` and `stderr.log`, then derives standard metrics
  such as log byte counts and artifact count from the recorded run files.
- Run comparison must never call adapter methods. It reads normalized
  `report.json`, logs, and artifact references from `.simtools/runs/`.
- Benchmark Runner v0.4 metadata and export paths must never call adapter
  methods. They read `benchmark_result`, `task_metrics`, reproducibility, and
  metrics fields from recorded reports only.

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
