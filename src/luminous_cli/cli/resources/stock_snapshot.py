"""Stock snapshot resource."""

from __future__ import annotations

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
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Get a point-in-time stock snapshot."""
    client = get_client()
    params: dict[str, str] = {
        "start_date": start_date,
        "end_date": end_date,
        "page": str(page),
        "per_page": str(per_page),
    }
    if warehouse_id is not None:
        params["warehouse_id"] = str(warehouse_id)

    data = client.request("GET", "/stock-snapshot", params=params)
    fmt = resolve_format(format)
    result = data.get("data", [])
    pagination = data.get("meta")
    render(result, columns=COLUMNS, pagination=pagination, fmt=fmt)
