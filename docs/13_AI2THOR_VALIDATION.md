# AI2-THOR Validation

This document records the first isolated AI2-THOR validation path.

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
.venv-ai2thor/bin/python -m simtools run ai2thor --mode smoke
.venv-ai2thor/bin/python -m simtools artifacts ai2thor
```

## Result

Validated on 2026-05-22:

- `doctor ai2thor`: installed
- `validate`: passed, 6 tools and 4 profiles
- dry-run smoke: planned
- real smoke: passed
- artifact screenshot: `.simtools/artifacts/ai2thor/smoke_20260522T090748Z.ppm`
- artifact report: `.simtools/artifacts/ai2thor/smoke_report_20260522T090749Z.json`

The screenshot was written as a PPM file to avoid adding image-writing
dependencies to SimTools.

## Notes

- This validation may download AI2-THOR runtime assets on first use.
- Do not run this in CI by default.
- Do not install AI2-THOR into the base SimTools environment.
