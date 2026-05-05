"""Customer returns resource."""

from __future__ import annotations

import typer

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="returns",
    singular="return",
    api_path="/returns",
    columns=[
        ("ID", "id", "dim"),
        ("Sales Order", "sales_order_id", ""),
        ("Status", "status", ""),
        ("Restock", "restock", ""),
        ("Type", "transaction_type", ""),
        ("Order Date", "order_date", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "delete"},
)

group = make_resource_group(spec)


@group.command("receive")
def returns_receive(
    return_id: int = typer.Argument(..., help="Return ID"),
) -> None:
    """Mark a customer return as received (PATCH)."""
    client = get_client()
    data = client.request("PATCH", f"/returns/{return_id}/receive")
    render_json(data)


@group.command("restock")
def returns_restock(
    return_id: int = typer.Argument(..., help="Return ID"),
    restock: bool = typer.Option(
        ..., "--restock/--no-restock", help="Whether the return should restock inventory"
    ),
) -> None:
    """Update the restock flag on a customer return (PATCH)."""
    client = get_client()
    data = client.request(
        "PATCH", f"/returns/{return_id}/restock", json_body={"restock": restock}
    )
    render_json(data)
