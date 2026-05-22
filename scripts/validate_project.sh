#!/usr/bin/env bash
set -euo pipefail

pytest
python -m simtools --help >/dev/null
python -m simtools list
python -m simtools status
python -m simtools real-status
python -m simtools profiles
python -m simtools compare
python -m simtools doctor
python -m simtools doctor ai2thor
python -m simtools doctor habitat
python -m simtools install-plan
python -m simtools install-plan ai2thor
python -m simtools run ai2thor --mode smoke --dry-run
python -m simtools run habitat --mode smoke --dry-run
python -m simtools view ai2thor --dry-run
python -m simtools artifacts
python -m simtools validate
python -m simtools ui --help >/dev/null
