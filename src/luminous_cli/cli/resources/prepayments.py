"""Prepayments resource."""

from __future__ import annotations

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
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="prepayments", help="Manage prepayments")

COLUMNS = [
    ("ID", "id", "dim"),
    ("Amount", "amount", "green"),
    ("Status", "status", ""),
    ("Vendor", "vendor_name", ""),
    ("Date", "created_at", "dim"),
]


@group.command("list")
def prepayment_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List prepayments."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/prepayments", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("create")
def prepayment_create(
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create a new prepayment."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/prepayments", json_body=payload)
    render_json(data)


@group.command("apply")
def prepayment_apply(
    prepayment_id: int = typer.Argument(..., help="Prepayment ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Apply a prepayment to a bill or payment obligation."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", f"/prepayments/{prepayment_id}/apply", json_body=payload)
    render_json(data)


@group.command("reverse")
def prepayment_reverse(
    prepayment_id: int = typer.Argument(..., help="Prepayment ID"),
    application_id: int = typer.Argument(..., help="Application ID to reverse"),
) -> None:
    """Reverse a prepayment application."""
    client = get_client()
    client.request("POST", f"/prepayments/{prepayment_id}/applications/{application_id}/reverse")
    typer.echo(f"Reversed application {application_id}")
