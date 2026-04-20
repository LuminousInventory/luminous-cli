"""Warehouse groups resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="warehouse-groups",
    singular="warehouse group",
    api_path="/warehouse-groups",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Description", "description", ""),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
    update_method="PUT",
)

group = make_resource_group(spec)
