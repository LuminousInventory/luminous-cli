"""Bills resource with full lifecycle management."""

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
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="bills",
    singular="bill",
    api_path="/bills",
    columns=[
        ("ID", "id", "dim"),
        ("Vendor", "vendor_name", ""),
        ("Status", "status", ""),
        ("Total", "total", "green"),
        ("Paid", "total_paid", "green"),
        ("Due", "total_due", "yellow"),
        ("Bill Date", "bill_date", ""),
        ("Due Date", "due_date", ""),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

# Replace the factory-generated group with our own that has the existing commands
# plus all the bill-specific actions
group = make_resource_group(spec)


# --- Bill actions ---

@group.command("post")
def bill_post(
    bill_id: int = typer.Argument(..., help="Bill ID"),
) -> None:
    """Post a bill (finalize for payment)."""
    client = get_client()
    data = client.request("POST", f"/bills/{bill_id}/post")
    typer.echo(f"Posted bill {bill_id}")


@group.command("hold")
def bill_hold(
    bill_id: int = typer.Argument(..., help="Bill ID"),
) -> None:
    """Place a bill on hold."""
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/hold")
    typer.echo(f"Bill {bill_id} placed on hold")


@group.command("unhold")
def bill_unhold(
    bill_id: int = typer.Argument(..., help="Bill ID"),
) -> None:
    """Remove hold from a bill."""
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/unhold")
    typer.echo(f"Bill {bill_id} hold removed")


@group.command("reopen")
def bill_reopen(
    bill_id: int = typer.Argument(..., help="Bill ID"),
) -> None:
    """Reopen a posted/closed bill."""
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/reopen")
    typer.echo(f"Bill {bill_id} reopened")


@group.command("variance")
def bill_variance(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    format: FormatOption = None,
) -> None:
    """Get variance data for a bill."""
    client = get_client()
    data = client.request("GET", f"/bills/{bill_id}/variance")
    render_json(data)


@group.command("resolve-variance")
def bill_resolve_variance(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Resolve variance on a bill."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/resolve-variance", json_body=payload)
    typer.echo(f"Variance resolved for bill {bill_id}")


@group.command("auto-allocate")
def bill_auto_allocate(
    bill_id: int = typer.Argument(..., help="Bill ID"),
) -> None:
    """Automatically allocate bill line items."""
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/auto-allocate")
    typer.echo(f"Auto-allocated bill {bill_id}")


@group.command("duplicate-check")
def bill_duplicate_check(
    vendor_id: Optional[int] = typer.Option(None, "--vendor-id"),
    bill_number: Optional[str] = typer.Option(None, "--bill-number"),
    format: FormatOption = None,
) -> None:
    """Check for duplicate bills."""
    client = get_client()
    params: dict[str, str] = {}
    if vendor_id:
        params["vendor_id"] = str(vendor_id)
    if bill_number:
        params["bill_number"] = bill_number
    data = client.request("GET", "/bills/duplicate-check", params=params)
    render_json(data)


@group.command("summary")
def bill_summary(
    format: FormatOption = None,
) -> None:
    """Bills summary with totals and counts by status."""
    client = get_client()
    data = client.request("GET", "/bills/summary")
    render_json(data)


@group.command("inbox")
def bill_inbox(
    format: FormatOption = None,
) -> None:
    """Bills needing allocation attention."""
    client = get_client()
    data = client.request("GET", "/bills/allocation-inbox")
    render_json(data)


@group.command("by-vendor")
def bills_by_vendor(
    vendor_id: int = typer.Argument(..., help="Vendor (company) ID"),
    format: FormatOption = None,
) -> None:
    """List bills for a specific vendor."""
    client = get_client()
    data = client.request("GET", f"/bills/vendor/{vendor_id}")
    render_json(data)


@group.command("by-po")
def bills_by_po(
    po_id: int = typer.Argument(..., help="Purchase order ID"),
    format: FormatOption = None,
) -> None:
    """List bills for a specific purchase order."""
    client = get_client()
    data = client.request("GET", f"/bills/purchase-order/{po_id}")
    render_json(data)


# --- Bill payments ---

payments_app = typer.Typer(name="payments", help="Bill payments")


@payments_app.command("create")
def payment_create(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Record a payment against a bill."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", f"/bills/{bill_id}/payments", json_body=payload)
    render_json(data)


@payments_app.command("delete")
def payment_delete(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    payment_id: int = typer.Argument(..., help="Payment ID"),
    yes: YesOption = False,
) -> None:
    """Delete a bill payment."""
    if not yes:
        typer.confirm(f"Delete payment {payment_id} from bill {bill_id}?", abort=True)
    client = get_client()
    client.request("DELETE", f"/bills/{bill_id}/payments/{payment_id}")
    typer.echo(f"Deleted payment {payment_id}")


@payments_app.command("void")
def payment_void(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    payment_id: int = typer.Argument(..., help="Payment ID"),
) -> None:
    """Void a bill payment."""
    client = get_client()
    client.request("POST", f"/bills/{bill_id}/payments/{payment_id}/void")
    typer.echo(f"Voided payment {payment_id}")


group.add_typer(payments_app)

# --- Bill allocations ---

allocations_app = typer.Typer(name="allocations", help="Bill allocations")


@allocations_app.command("list")
def allocations_list(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    format: FormatOption = None,
) -> None:
    """List allocations for a bill."""
    client = get_client()
    data = client.request("GET", f"/bills/{bill_id}/allocations")
    render_json(data)


@allocations_app.command("create")
def allocation_create(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create an allocation for a bill."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", f"/bills/{bill_id}/allocations", json_body=payload)
    render_json(data)


@allocations_app.command("delete")
def allocation_delete(
    bill_id: int = typer.Argument(..., help="Bill ID"),
    allocation_id: int = typer.Argument(..., help="Allocation ID"),
    yes: YesOption = False,
) -> None:
    """Delete a bill allocation."""
    if not yes:
        typer.confirm(f"Delete allocation {allocation_id}?", abort=True)
    client = get_client()
    client.request("DELETE", f"/bills/{bill_id}/allocations/{allocation_id}")
    typer.echo(f"Deleted allocation {allocation_id}")


group.add_typer(allocations_app)


@group.command("aging")
def bills_aging(
    format: FormatOption = None,
) -> None:
    """AP bills aging report grouped by vendor."""
    client = get_client()
    data = client.request("GET", "/bills/reports/aging")
    render_json(data)
