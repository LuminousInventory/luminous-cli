"""Sales orders resource with shipments subresource."""

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
from luminous_cli.cli.resources._custom_fields import make_custom_fields_group
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.cli.resources._tags import make_tags_group
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

spec = ResourceSpec(
    name="sales-orders",
    singular="sales order",
    api_path="/sales-orders",
    columns=[
        ("ID", "id", "dim"),
        ("Order #", "order_number", "cyan"),
        ("Status", "order_status", ""),
        ("Company", "company.name", ""),
        ("Date", "order_date", ""),
        ("Total", "total", "green"),
        ("Qty", "total_order_quantity", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update"},
    update_method="PATCH",
)

group = make_resource_group(spec)
group.add_typer(make_tags_group("sales-orders"))
group.add_typer(make_custom_fields_group("sales-orders"))

# --- Shipments subresource ---

shipments_app = typer.Typer(name="shipments", help="Manage shipments for a sales order")


@shipments_app.command("list")
def shipments_list(
    order_id: int = typer.Argument(..., help="Sales order ID"),
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List shipments for a sales order."""
    client = get_client()
    qp = QueryParams(page=page, per_page=per_page)
    resp = client.list(f"/sales-orders/{order_id}/shipments", params=qp)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("Tracking", "tracking_number", "cyan"),
        ("Carrier", "carrier_code", ""),
        ("Ship Date", "ship_date", ""),
        ("Status", "status", ""),
        ("Items", "items_count", ""),
    ]
    render(resp.data, columns=columns, pagination=resp.pagination, fmt=fmt)


@shipments_app.command("create")
def shipments_create(
    order_id: int = typer.Argument(..., help="Sales order ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create a shipment for a sales order."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo(
            "Provide shipment data via --json or --file.\n"
            "Example: luminous sales-orders shipments create 123 --file shipment.json",
            err=True,
        )
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request(
        "POST", f"/sales-orders/{order_id}/shipments", json_body=payload
    )
    result = data.get("data", data)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("Tracking", "tracking_number", "cyan"),
        ("Carrier", "carrier_code", ""),
        ("Ship Date", "ship_date", ""),
    ]
    render(result, columns=columns, fmt=fmt)


@shipments_app.command("add-packages")
def shipments_add_packages(
    order_id: int = typer.Argument(..., help="Sales order ID"),
    shipment_id: int = typer.Argument(..., help="Shipment ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create packages for a shipment."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo("Provide package data via --json or --file.", err=True)
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request(
        "POST",
        f"/sales-orders/{order_id}/shipments/{shipment_id}/packages",
        json_body=payload,
    )
    result = data.get("data", data)
    fmt = resolve_format(format)
    render(result, columns=[("ID", "id", "dim")], fmt=fmt)


@shipments_app.command("force-push-source-fulfillment")
def shipments_force_push_source_fulfillment(
    order_id: int = typer.Argument(..., help="Sales order ID"),
    shipment_id: int = typer.Argument(..., help="Shipment ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Force-push shipment fulfillment back to the order source."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo(
            "Provide payload via --json or --file. "
            "Required: sales_order_item_ids. Optional: tracking_number, carrier.",
            err=True,
        )
        raise typer.Exit(code=1)
    client = get_client()
    data = client.request(
        "POST",
        f"/sales-orders/{order_id}/shipments/{shipment_id}/force-push-source-fulfillment",
        json_body=payload,
    )
    from luminous_cli.output.json_out import render_json
    render_json(data)


@shipments_app.command("billable-lines")
def shipments_billable_lines(
    shipment_id: int = typer.Argument(..., help="Shipment ID"),
    format: FormatOption = None,
) -> None:
    """Get billable lines for a shipment."""
    from luminous_cli.output.json_out import render_json
    client = get_client()
    data = client.request("GET", f"/shipments/{shipment_id}/billable-lines")
    render_json(data)


group.add_typer(shipments_app)

# --- Export command ---


@group.command("export")
def export_cmd(
    filter: FilterOption = None,
    sort: SortOption = None,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Export sales orders (incremental, cursor-based)."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, per_page=per_page)
    resp = client.list("/sales-orders/export", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=spec.columns, pagination=resp.pagination, fmt=fmt)
