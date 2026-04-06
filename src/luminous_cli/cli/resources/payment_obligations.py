"""Payment obligations resource."""

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
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="payment-obligations", help="Payment obligations")

COLUMNS = [
    ("ID", "id", "dim"),
    ("Status", "status", ""),
    ("Amount", "amount", "green"),
    ("Due Date", "due_date", ""),
    ("Vendor", "vendor_name", ""),
]


@group.command("list")
def po_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List payment obligations."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/payment-obligations", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("get")
def po_get(
    obligation_id: int = typer.Argument(..., help="Payment obligation ID"),
    format: FormatOption = None,
) -> None:
    """Get a payment obligation."""
    client = get_client()
    data = client.get("/payment-obligations", obligation_id)
    fmt = resolve_format(format)
    render(data, columns=COLUMNS, fmt=fmt)


@group.command("update")
def po_update(
    obligation_id: int = typer.Argument(..., help="Payment obligation ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Update a payment obligation."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.update("/payment-obligations", obligation_id, payload)
    render_json(data)


@group.command("dashboard")
def po_dashboard(format: FormatOption = None) -> None:
    """Payment obligations dashboard summary."""
    client = get_client()
    data = client.request("GET", "/payment-obligations/dashboard")
    render_json(data)


@group.command("link-bill")
def po_link_bill(
    obligation_id: int = typer.Argument(..., help="Payment obligation ID"),
    bill_id: int = typer.Argument(..., help="Bill ID to link"),
) -> None:
    """Link a bill to a payment obligation."""
    client = get_client()
    client.request("POST", f"/payment-obligations/{obligation_id}/link-bill", json_body={"bill_id": bill_id})
    typer.echo(f"Linked bill {bill_id} to obligation {obligation_id}")


@group.command("unlink-bill")
def po_unlink_bill(
    obligation_id: int = typer.Argument(..., help="Payment obligation ID"),
    bill_id: int = typer.Argument(..., help="Bill ID to unlink"),
) -> None:
    """Unlink a bill from a payment obligation."""
    client = get_client()
    client.request("POST", f"/payment-obligations/{obligation_id}/unlink-bill", json_body={"bill_id": bill_id})
    typer.echo(f"Unlinked bill {bill_id} from obligation {obligation_id}")
