"""Rich table output with nested field flattening."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

stdout = Console()


def _resolve_path(obj: dict[str, Any], path: str) -> Any:
    """Resolve a dot-separated path like 'warehouse.name' into a value."""
    value: Any = obj
    for part in path.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            idx = int(part)
            value = value[idx] if idx < len(value) else None
        else:
            return None
    return value


def _format_value(value: Any) -> str:
    """Format a value for table display."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        items = [str(v) for v in value[:5]]
        text = ", ".join(items)
        if len(value) > 5:
            text += f" (+{len(value) - 5} more)"
        return text
    if isinstance(value, dict):
        return "{...}"
    return str(value)


def render_table(
    data: list[dict[str, Any]],
    columns: list[tuple[str, str, str]],
    pagination: dict[str, Any] | None = None,
) -> None:
    """Render data as a Rich table.

    Args:
        data: List of record dicts.
        columns: List of (header, dot_path, style) tuples.
        pagination: Optional pagination info dict from API.
    """
    table = Table(show_lines=False, pad_edge=True)
    for header, _, style in columns:
        table.add_column(header, style=style or None, no_wrap=(header in ("ID", "SKU")))

    for obj in data:
        row = []
        for _, path, _ in columns:
            value = _resolve_path(obj, path)
            row.append(_format_value(value))
        table.add_row(*row)

    stdout.print(table)

    if pagination:
        current = pagination.get("current_page", 1)
        last = pagination.get("last_page", 1)
        total = pagination.get("total", len(data))
        stdout.print(f"[dim]Page {current} of {last} ({total} total)[/dim]")
