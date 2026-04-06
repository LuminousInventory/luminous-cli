"""Consumption report resource."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FilterOption, FormatOption, PageOption, PerPageOption, SortOption
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

group = typer.Typer(name="consumption", help="Inventory consumption reports")

COLUMNS = [
    ("Date", "date", ""),
    ("Product", "product", ""),
    ("Quantity", "quantity", "green"),
]


@group.command("list")
def consumption_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Get paginated consumption report data."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/inventory/transactions/consumption", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("export")
def consumption_export(
    filter: FilterOption = None,
    format: FormatOption = None,
) -> None:
    """Export consumption report."""
    client = get_client()
    params: dict[str, str] = {}
    # Pass through any filters as raw query params
    if filter:
        qp = QueryParams.from_cli_args(raw_filters=filter)
        params = qp.filters

    data = client.request("GET", "/inventory/transactions/consumption/export", params=params)
    fmt = resolve_format(format)
    result = data.get("data", data)
    if isinstance(result, list):
        render(result, columns=COLUMNS, fmt=fmt)
    else:
        render(result, columns=COLUMNS, fmt=fmt)
