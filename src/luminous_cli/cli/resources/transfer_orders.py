"""Transfer orders resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="transfer-orders",
    singular="transfer order",
    api_path="/transfer-orders",
    columns=[
        ("ID", "id", "dim"),
        ("Number", "number", "cyan"),
        ("Status", "status", ""),
        ("Source", "source_warehouse.name", ""),
        ("Destination", "destination_warehouse.name", ""),
        ("Date", "date", ""),
        ("Arrival", "arrival_date", ""),
    ],
    capabilities={"list", "get", "create"},
)

group = make_resource_group(spec)
