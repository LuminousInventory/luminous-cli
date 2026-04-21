"""Vendor credits resource."""

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

group = typer.Typer(name="vendor-credits", help="Manage vendor credits")

COLUMNS = [
    ("ID", "id", "dim"),
    ("Vendor", "vendor_name", ""),
    ("Amount", "amount", "green"),
    ("Status", "status", ""),
    ("Date", "created_at", "dim"),
]


@group.command("list")
def vc_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List vendor credits."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/vendor-credits", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("get")
def vc_get(
    credit_id: int = typer.Argument(..., help="Vendor credit ID"),
    format: FormatOption = None,
) -> None:
    """Get a vendor credit."""
    client = get_client()
    data = client.get("/vendor-credits", credit_id)
    fmt = resolve_format(format)
    render(data, columns=COLUMNS, fmt=fmt)


@group.command("create")
def vc_create(
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create a vendor credit."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/vendor-credits", json_body=payload)
    render_json(data)


@group.command("apply")
def vc_apply(
    credit_id: int = typer.Argument(..., help="Vendor credit ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Apply a vendor credit to a bill or payment obligation."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", f"/vendor-credits/{credit_id}/apply", json_body=payload)
    render_json(data)


@group.command("cancel")
def vc_cancel(
    credit_id: int = typer.Argument(..., help="Vendor credit ID"),
    yes: YesOption = False,
) -> None:
    """Cancel a vendor credit."""
    if not yes:
        typer.confirm(f"Cancel vendor credit {credit_id}?", abort=True)
    client = get_client()
    client.request("POST", f"/vendor-credits/{credit_id}/cancel")
    typer.echo(f"Cancelled vendor credit {credit_id}")


@group.command("reverse")
def vc_reverse(
    credit_id: int = typer.Argument(..., help="Vendor credit ID"),
    application_id: int = typer.Argument(..., help="Application ID to reverse"),
) -> None:
    """Reverse a vendor credit application."""
    client = get_client()
    client.request("POST", f"/vendor-credits/{credit_id}/applications/{application_id}/reverse")
    typer.echo(f"Reversed application {application_id}")


@group.command("delete-application")
def vc_delete_application(
    credit_id: int = typer.Argument(..., help="Vendor credit ID"),
    application_id: int = typer.Argument(..., help="Application ID"),
    yes: YesOption = False,
) -> None:
    """Delete a vendor credit application."""
    if not yes:
        typer.confirm(f"Delete application {application_id}?", abort=True)
    client = get_client()
    client.request("DELETE", f"/vendor-credits/{credit_id}/applications/{application_id}")
    typer.echo(f"Deleted application {application_id}")


@group.command("vendor-statement")
def vendor_statement(
    vendor_id: int = typer.Argument(..., help="Vendor (company) ID"),
    format: FormatOption = None,
) -> None:
    """Get a vendor statement (via vendor-credits endpoint)."""
    client = get_client()
    data = client.request("GET", f"/vendor-credits/vendor/{vendor_id}/statement")
    render_json(data)


@group.command("statement")
def vendor_statement_direct(
    vendor_id: int = typer.Argument(..., help="Vendor (company) ID"),
    format: FormatOption = None,
) -> None:
    """Get a vendor statement."""
    client = get_client()
    data = client.request("GET", f"/vendors/{vendor_id}/statement")
    render_json(data)
