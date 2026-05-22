"""Shell formatting helpers."""

from __future__ import annotations


def join_commands(commands: list[str]) -> str:
    return "\n".join(commands)
