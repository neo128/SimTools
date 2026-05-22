# CLI Spec

The CLI is implemented with Typer and Rich.

## Commands

```bash
simtools --help
simtools list
simtools list --category indoor_interaction
simtools list --installed
simtools info ai2thor
simtools status
simtools profiles
simtools doctor
simtools doctor ai2thor
simtools compare
simtools compare --format table
simtools compare --format markdown
simtools install-plan
simtools install-plan ai2thor
simtools run ai2thor --mode smoke
simtools run ai2thor --mode smoke --dry-run
simtools view ai2thor --dry-run
simtools view ai2thor --execute --scene FloorPlan1
simtools view ai2thor --execute --scene FloorPlan1 --max-actions 0
simtools view ai2thor --ui --execute --scene FloorPlan1 --port 8502
simtools artifacts
simtools artifacts ai2thor
simtools validate
simtools ui
```

## Rules

- CLI commands read the registry and adapters.
- CLI commands must not import real simulator packages at startup.
- Mutating commands must support dry-run.
- Missing tools should show valid tool ids.
- Missing simulator packages should produce clear installation next steps.
- `install-plan` prints commands only and never executes installers.
- `run` stores non-dry-run reports under `.simtools/artifacts/<tool_id>/`.
- `view` is dry-run by default and requires `--execute` for GUI behavior.
- `view --ui` starts a mouse-driven local UI when the adapter supports it.
