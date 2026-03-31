"""Locations resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="locations",
    singular="location",
    api_path="/locations",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Status", "status", ""),
        ("Pick Location", "is_pick_location", ""),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
