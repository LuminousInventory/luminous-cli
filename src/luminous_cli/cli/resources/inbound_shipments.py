"""Inbound shipments resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="inbound-shipments",
    singular="inbound shipment",
    api_path="/inbound-shipments",
    columns=[
        ("ID", "id", "dim"),
        ("Status", "status", ""),
        ("Carrier", "carrier", ""),
        ("Tracking", "tracking_number", "cyan"),
        ("Expected", "expected_date", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
