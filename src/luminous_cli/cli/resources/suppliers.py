"""Suppliers resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="suppliers",
    singular="supplier",
    api_path="/suppliers",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Email", "email", ""),
        ("Phone", "phone", ""),
        ("Status", "status", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)
