"""Purchase orders resource with payments subresource."""

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
    YesOption,
)
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

spec = ResourceSpec(
    name="purchase-orders",
    singular="purchase order",
    api_path="/purchase-orders",
    columns=[
        ("ID", "id", "dim"),
        ("PO #", "order_numbers", "cyan"),
        ("Status", "order_status", ""),
        ("Supplier", "supplier.name", ""),
        ("Date", "order_date", ""),
        ("Qty", "total_qty_ordered", ""),
        ("Total", "total_cost", "green"),
        ("Paid", "total_paid", "green"),
        ("Due", "total_due", "yellow"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
    update_method="PUT",
)

group = make_resource_group(spec)

# --- PO Items list ---


@group.command("items")
def po_items_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List purchase order items across all POs."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/purchase-orders/items", params=qp)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("PO ID", "purchase_order_id", ""),
        ("SKU", "product.sku", "cyan"),
        ("Product", "product.name", ""),
        ("Qty", "quantity", ""),
        ("Price", "unit_price", "green"),
    ]
    render(resp.data, columns=columns, pagination=resp.pagination, fmt=fmt)


# --- Payments subresource ---

payments_app = typer.Typer(name="payments", help="Manage purchase order payments")


@payments_app.command("create")
def payment_create(
    po_id: int = typer.Argument(..., help="Purchase order ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    payment_date: Optional[str] = typer.Option(None, "--payment-date"),
    payment_type: Optional[str] = typer.Option(None, "--payment-type", help="cash|credit_card|debit_card|check|bank_transfer"),
    paid_amount: Optional[float] = typer.Option(None, "--paid-amount"),
    remarks: Optional[str] = typer.Option(None, "--remarks"),
    format: FormatOption = None,
) -> None:
    """Create a payment for a purchase order."""
    flags = {
        "payment_date": payment_date,
        "payment_type": payment_type,
        "paid_amount": paid_amount,
        "remarks": remarks,
    }
    payload = resolve_input(json_input=json_input, file_input=file, flags=flags)
    if not payload:
        typer.echo("Provide payment data via flags, --json, or --file.", err=True)
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request("POST", f"/purchase-orders/{po_id}/payments", json_body=payload)
    result = data.get("data", data)
    fmt = resolve_format(format)
    columns = [("ID", "id", "dim"), ("Date", "payment_date", ""), ("Type", "payment_type", ""), ("Amount", "paid_amount", "green")]
    render(result, columns=columns, fmt=fmt)


@payments_app.command("update")
def payment_update(
    po_id: int = typer.Argument(..., help="Purchase order ID"),
    payment_id: int = typer.Argument(..., help="Payment ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    payment_date: Optional[str] = typer.Option(None, "--payment-date"),
    payment_type: Optional[str] = typer.Option(None, "--payment-type"),
    paid_amount: Optional[float] = typer.Option(None, "--paid-amount"),
    remarks: Optional[str] = typer.Option(None, "--remarks"),
    format: FormatOption = None,
) -> None:
    """Update a purchase order payment."""
    flags = {
        "payment_date": payment_date,
        "payment_type": payment_type,
        "paid_amount": paid_amount,
        "remarks": remarks,
    }
    payload = resolve_input(json_input=json_input, file_input=file, flags=flags)
    if not payload:
        typer.echo("Nothing to update.", err=True)
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request("PUT", f"/purchase-orders/{po_id}/payments/{payment_id}", json_body=payload)
    result = data.get("data", data)
    fmt = resolve_format(format)
    render(result, columns=[("ID", "id", "dim"), ("Amount", "paid_amount", "green")], fmt=fmt)


@payments_app.command("delete")
def payment_delete(
    po_id: int = typer.Argument(..., help="Purchase order ID"),
    payment_id: int = typer.Argument(..., help="Payment ID"),
    yes: YesOption = False,
) -> None:
    """Delete a purchase order payment."""
    if not yes:
        typer.confirm(f"Delete payment {payment_id} from PO {po_id}?", abort=True)
    client = get_client()
    client.request("DELETE", f"/purchase-orders/{po_id}/payments/{payment_id}")
    typer.echo(f"Deleted payment {payment_id}")


group.add_typer(payments_app)
