#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${SIMTOOLS_AI2THOR_PYTHON:-.venv-ai2thor/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "AI2-THOR validation Python not found: $PYTHON_BIN" >&2
  echo "Create it with:" >&2
  echo "  conda create -p ./.venv-ai2thor python=3.11 pip -y" >&2
  echo "  .venv-ai2thor/bin/python -m pip install -e . ai2thor" >&2
  exit 2
fi

"$PYTHON_BIN" -m simtools doctor ai2thor
"$PYTHON_BIN" -m simtools validate
"$PYTHON_BIN" -m simtools run ai2thor --mode smoke --dry-run
"$PYTHON_BIN" -m simtools run ai2thor --mode smoke
"$PYTHON_BIN" -m simtools artifacts ai2thor
