"""Receiving reports resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

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
