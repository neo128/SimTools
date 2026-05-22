#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m simtools run ai2thor --mode smoke --dry-run
