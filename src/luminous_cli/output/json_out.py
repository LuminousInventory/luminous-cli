"""JSON and NDJSON output."""

from __future__ import annotations

import sys
from typing import Any

import orjson


def render_json(data: list[dict[str, Any]] | dict[str, Any]) -> None:
    """Pretty-printed JSON to stdout."""
    sys.stdout.buffer.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()


def render_ndjson(data: list[dict[str, Any]]) -> None:
    """One JSON object per line."""
    for obj in data:
        sys.stdout.buffer.write(orjson.dumps(obj))
        sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
