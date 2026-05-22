# Plan 003: First AI2-THOR Adapter

## Goal

Add the first real opt-in adapter path for AI2-THOR while keeping the base tests
simulator-free.

## Steps

1. Keep `check_installed()` based on `importlib.util.find_spec`.
2. Return skipped smoke results when AI2-THOR is missing.
3. Lazy import `ai2thor.controller.Controller` only inside the real smoke path.
4. Write artifacts under `.simtools/artifacts/ai2thor/`.
5. Keep install behavior as an install plan, not automatic execution.

## Verification

```bash
pytest
python -m simtools install-plan ai2thor
python -m simtools doctor ai2thor
python -m simtools run ai2thor --mode smoke --dry-run
```
