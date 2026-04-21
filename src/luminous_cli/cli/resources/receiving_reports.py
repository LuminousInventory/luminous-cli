"""Receiving reports resource."""

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="receiving-reports",
    singular="receiving report",
    api_path="/receiving-reports",
    columns=[
        ("ID", "id", "dim"),
        ("PO ID", "purchase_order_id", ""),
        ("Status", "status", ""),
        ("Date", "received_date", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create"},
)

group = make_resource_group(spec)


@group.command("billable-lines")
def rr_billable_lines(
    rr_id: int = typer.Argument(..., help="Receiving report ID"),
    format: FormatOption = None,
) -> None:
    """Get billable lines for a receiving report."""
    client = get_client()
    data = client.request("GET", f"/receiving-reports/{rr_id}/billable-lines")
    render_json(data)
