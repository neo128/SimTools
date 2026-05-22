"""Small process execution helper with dry-run support."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessResult:
    command: str
    dry_run: bool
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


def run_command(command: str, dry_run: bool = True) -> ProcessResult:
    if dry_run:
        return ProcessResult(command=command, dry_run=True)
    completed = subprocess.run(
        shlex.split(command),
        check=False,
        capture_output=True,
        text=True,
    )
    return ProcessResult(
        command=command,
        dry_run=False,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
