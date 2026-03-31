"""CSV output."""

from __future__ import annotations

import csv
import sys
from typing import Any


def render_csv(
    data: list[dict[str, Any]],
    columns: list[tuple[str, str, str]],
) -> None:
    """Render data as CSV using the column specs for headers and paths."""
    writer = csv.writer(sys.stdout)

    # Header row
    writer.writerow([header for header, _, _ in columns])

    # Data rows
    for obj in data:
        row = []
        for _, path, _ in columns:
            value = obj
            for part in path.split("."):
                if isinstance(value, dict):
                    value = value.get(part, "")
                else:
                    value = ""
                    break
            if isinstance(value, (list, dict)):
                import orjson
                value = orjson.dumps(value).decode()
            row.append(value if value is not None else "")
        writer.writerow(row)
