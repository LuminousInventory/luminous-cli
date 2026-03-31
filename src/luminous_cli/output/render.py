"""Unified render dispatcher."""

from __future__ import annotations

from typing import Any


def render(
    data: list[dict[str, Any]] | dict[str, Any],
    *,
    columns: list[tuple[str, str, str]],
    pagination: dict[str, Any] | None = None,
    fmt: str = "table",
) -> None:
    """Single entry point for all output formatting.

    Args:
        data: Response data (single dict or list of dicts).
        columns: List of (header, dot_path, style) tuples for table/CSV.
        pagination: Pagination info from API response.
        fmt: Output format (table, json, ndjson, csv).
    """
    # Normalize single objects to list for uniform handling
    is_single = isinstance(data, dict)
    if is_single:
        data = [data]
        pagination = None

    match fmt:
        case "table":
            from luminous_cli.output.table import render_table
            render_table(data, columns, pagination)
        case "json":
            from luminous_cli.output.json_out import render_json
            render_json(data[0] if is_single else data)
        case "ndjson":
            from luminous_cli.output.json_out import render_ndjson
            render_ndjson(data)
        case "csv":
            from luminous_cli.output.csv_out import render_csv
            render_csv(data, columns)
        case _:
            raise ValueError(f"Unknown format: {fmt}")
