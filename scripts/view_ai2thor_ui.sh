#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${SIMTOOLS_AI2THOR_PYTHON:-.venv-ai2thor/bin/python}"
SCENE="${1:-FloorPlan1}"
if [[ $# -gt 0 ]]; then
  shift
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "AI2-THOR validation Python not found: $PYTHON_BIN" >&2
  echo "Create it with:" >&2
  echo "  conda create -p ./.venv-ai2thor python=3.11 pip -y" >&2
  echo "  .venv-ai2thor/bin/python -m pip install -e . ai2thor streamlit" >&2
  exit 2
fi

"$PYTHON_BIN" -m simtools view ai2thor --ui --execute --scene "$SCENE" "$@"
