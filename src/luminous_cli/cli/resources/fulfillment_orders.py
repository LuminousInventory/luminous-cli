"""Fulfillment orders resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FileOption, FormatOption, JsonOption
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="fulfillment-orders",
    singular="fulfillment order",
    api_path="/fulfillment-orders",
    columns=[
        ("ID", "id", "dim"),
        ("Status", "status", ""),
        ("Order", "sales_order.order_number", "cyan"),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)


@group.command("push")
def fo_push(
    fulfillment_order_id: int = typer.Argument(..., help="Fulfillment order ID"),
    debug: bool = typer.Option(False, "--debug", help="Capture per-request HTTP debug payload"),
) -> None:
    """Push a fulfillment order to its destination OMS."""
    client = get_client()
    body: dict = {"debug": True} if debug else {}
    data = client.request(
        "POST", f"/fulfillment-orders/{fulfillment_order_id}/push", json_body=body
    )
    render_json(data)


@group.command("unpush")
def fo_unpush(
    fulfillment_order_id: int = typer.Argument(..., help="Fulfillment order ID"),
    debug: bool = typer.Option(False, "--debug", help="Capture per-request HTTP debug payload"),
) -> None:
    """Unpush a fulfillment order from its destination OMS."""
    client = get_client()
    body: dict = {"debug": True} if debug else {}
    data = client.request(
        "POST", f"/fulfillment-orders/{fulfillment_order_id}/unpush", json_body=body
    )
    render_json(data)


@group.command("create-shipment")
def fo_create_shipment(
    fulfillment_order_id: int = typer.Argument(..., help="Fulfillment order ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Create a carrier shipment bound to a fulfillment order."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo("Provide shipment data via --json or --file.", err=True)
        raise typer.Exit(code=1)

    client = get_client()
    data = client.request(
        "POST",
        f"/fulfillment-orders/{fulfillment_order_id}/shipments",
        json_body=payload,
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
