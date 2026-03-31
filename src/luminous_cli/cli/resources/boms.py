"""BOMs (Bills of Materials) resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="boms",
    singular="BOM",
    api_path="/boms",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)
