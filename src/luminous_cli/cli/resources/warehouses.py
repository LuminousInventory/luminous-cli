"""Warehouses resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="warehouses",
    singular="warehouse",
    api_path="/warehouses",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Status", "status", ""),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
