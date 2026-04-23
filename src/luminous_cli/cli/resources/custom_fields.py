"""Custom field definitions resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="custom-fields",
    singular="custom field",
    api_path="/custom-fields",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Type", "type", ""),
        ("Model", "model", ""),
        ("Required", "required", ""),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
    update_method="PUT",
)

group = make_resource_group(spec)
