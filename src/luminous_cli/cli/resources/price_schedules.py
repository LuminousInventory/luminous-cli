"""Price schedules resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="price-schedules",
    singular="price schedule",
    api_path="/price-schedules",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Type", "type", ""),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
