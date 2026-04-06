"""Inventory aging resource."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FilterOption, FormatOption, PageOption, PerPageOption, SortOption
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

group = typer.Typer(name="inventory-aging", help="Inventory aging reports")

COLUMNS = [
    ("Product ID", "product_id", "dim"),
    ("SKU", "sku", "cyan"),
    ("Name", "product_name", ""),
    ("Category", "category", ""),
]


@group.command("list")
def aging_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Get paginated inventory aging data."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/inventory/aging", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("export")
def aging_export(
    filter: FilterOption = None,
) -> None:
    """Export inventory aging report as CSV or Excel."""
    client = get_client()
    params: dict[str, str] = {}
    if filter:
        qp = QueryParams.from_cli_args(raw_filters=filter)
        params = qp.filters
    data = client.request("GET", "/inventory/aging/export", params=params)
    from luminous_cli.output.json_out import render_json
    render_json(data)
