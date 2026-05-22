# Plan Template

## Goal

State the smallest useful outcome.

## Scope

In scope:

- item

Out of scope:

- heavy simulator installation
- large asset download
- GUI launch in tests

## Steps

1. Read constraints and relevant docs.
2. Update docs or manifests.
3. Implement code.
4. Add or update tests.
5. Run verification commands.
6. Summarize risks and next steps.

## Verification

```bash
pytest
python -m simtools list
python -m simtools compare
python -m simtools doctor
```
