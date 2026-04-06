"""Vendor returns resource."""

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
    YesOption,
)
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="vendor-returns", help="Manage vendor returns")

COLUMNS = [
    ("ID", "id", "dim"),
    ("Vendor", "vendor_name", ""),
    ("Status", "status", ""),
    ("Date", "created_at", "dim"),
]


@group.command("list")
def vr_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List vendor returns."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/vendor-returns", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("get")
def vr_get(
    return_id: int = typer.Argument(..., help="Vendor return ID"),
    format: FormatOption = None,
) -> None:
    """Get a vendor return."""
    client = get_client()
    data = client.get("/vendor-returns", return_id)
    fmt = resolve_format(format)
    render(data, columns=COLUMNS, fmt=fmt)


@group.command("create")
def vr_create(
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create a vendor return."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/vendor-returns", json_body=payload)
    render_json(data)


@group.command("process")
def vr_process(
    return_id: int = typer.Argument(..., help="Vendor return ID"),
) -> None:
    """Process a vendor return."""
    client = get_client()
    client.request("POST", f"/vendor-returns/{return_id}/process")
    typer.echo(f"Processed vendor return {return_id}")


@group.command("cancel")
def vr_cancel(
    return_id: int = typer.Argument(..., help="Vendor return ID"),
    yes: YesOption = False,
) -> None:
    """Cancel a vendor return."""
    if not yes:
        typer.confirm(f"Cancel vendor return {return_id}?", abort=True)
    client = get_client()
    client.request("POST", f"/vendor-returns/{return_id}/cancel")
    typer.echo(f"Cancelled vendor return {return_id}")


@group.command("generate-credit")
def vr_generate_credit(
    return_id: int = typer.Argument(..., help="Vendor return ID"),
) -> None:
    """Generate a vendor credit from a return."""
    client = get_client()
    data = client.request("POST", f"/vendor-returns/{return_id}/generate-credit")
    render_json(data)
