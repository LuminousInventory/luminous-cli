"""TTY detection and format resolution."""

from __future__ import annotations

import sys


def resolve_format(explicit: str | None = None, default: str = "table") -> str:
    """Determine output format.

    Priority: explicit flag > TTY detection > default.
    Non-TTY (piped) defaults to json for machine consumption.
    """
    if explicit:
        return explicit
    if not sys.stdout.isatty():
        return "json"
    return default
