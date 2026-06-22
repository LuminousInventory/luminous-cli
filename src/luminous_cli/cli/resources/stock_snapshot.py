"""Stock snapshot resource."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer

from luminous_cli.cli._options import FilterOption, FormatOption, PageOption, PerPageOption
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

group = typer.Typer(name="stock-snapshot", help="Point-in-time stock snapshots")

COLUMNS = [
    ("Product ID", "product_id", "dim"),
    ("SKU", "sku", "cyan"),
    ("Name", "name", ""),
    ("On Hand", "qty_onhand", "green"),
    ("Available", "qty_available", "green"),
    ("Warehouse", "warehouse_name", ""),
]


@group.command("get")
def snapshot_get(
    start_date: str = typer.Option(..., "--start-date", help="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: str = typer.Option(..., "--end-date", help="End date (YYYY-MM-DD HH:MM:SS)"),
    warehouse_id: Optional[int] = typer.Option(None, "--warehouse-id", help="Filter by warehouse ID"),
    filter: FilterOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Get a point-in-time stock snapshot."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, page=page, per_page=per_page)
    params = qp.to_dict()
    params["start_date"] = start_date
    params["end_date"] = end_date
    if warehouse_id is not None:
        params["warehouse_id"] = str(warehouse_id)

    data = client.request("GET", "/stock-snapshot", params=params)
    fmt = resolve_format(format)
    result = data.get("data", [])
    pagination = data.get("meta")
    render(result, columns=COLUMNS, pagination=pagination, fmt=fmt)


@group.command("export")
def snapshot_export(
    start_date: str = typer.Option(..., "--start-date", help="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: str = typer.Option(..., "--end-date", help="End date (YYYY-MM-DD HH:MM:SS)"),
    warehouse_id: Optional[int] = typer.Option(None, "--warehouse-id", help="Filter by warehouse ID"),
    filter: FilterOption = None,
    export: str = typer.Option("csv", "--export", help="Export format: csv|excel"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Export a point-in-time stock snapshot as CSV or Excel."""
    if export not in {"csv", "excel"}:
        raise typer.BadParameter("Export format must be csv or excel")

    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter)
    params = dict(qp.filters)
    params["start_date"] = start_date
    params["end_date"] = end_date
    params["export"] = export
    if warehouse_id is not None:
        params["warehouse_id"] = str(warehouse_id)

    response = client.download("GET", "/stock-snapshot", params=params)
    if response.status_code == 202 or "application/json" in response.headers.get("Content-Type", ""):
        typer.echo(response.text)
        raise typer.Exit(code=1)

    output_path = output or Path(_filename_from_disposition(response.headers.get("Content-Disposition"), export))
    output_path.write_bytes(response.content)
    typer.echo(f"Wrote {output_path}")


def _filename_from_disposition(content_disposition: str | None, export: str) -> str:
    if content_disposition:
        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if match:
            return match.group(1)

    suffix = "xlsx" if export == "excel" else "csv"
    return f"stock-snapshot.{suffix}"
