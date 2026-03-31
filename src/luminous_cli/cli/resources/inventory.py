"""Inventory resource (stocks + adjustments)."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import (
    FileOption,
    FilterOption,
    FormatOption,
    JsonOption,
    PageOption,
    PerPageOption,
    SortOption,
)
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

group = typer.Typer(name="inventory", help="Manage inventory")


@group.command("stocks")
def stocks_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List inventory stock levels."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/inventory/stocks", params=qp)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("SKU", "sku", "cyan"),
        ("Name", "name", ""),
        ("Type", "type", ""),
        ("On Hand", "qty_onhand", "green"),
        ("Available", "qty_available", "green"),
        ("Pending", "qty_pending", "yellow"),
        ("Incoming", "qty_incoming", ""),
    ]
    render(resp.data, columns=columns, pagination=resp.pagination, fmt=fmt)


@group.command("adjust")
def adjust(
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create an inventory adjustment."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo(
            "Provide adjustment data via --json or --file.\n"
            'Example: luminous inventory adjust --json \'{"adjustment_entries": [...]}\'',
            err=True,
        )
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request("POST", "/inventory/adjustments", json_body=payload)
    result = data.get("data", data)
    fmt = resolve_format(format)
    render(result, columns=[("ID", "id", "dim"), ("Remarks", "remarks", "")], fmt=fmt)
