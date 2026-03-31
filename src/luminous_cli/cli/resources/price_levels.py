"""Price levels resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="price-levels",
    singular="price level",
    api_path="/price-levels",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Type", "type", ""),
        ("% Increase", "percent_increase", ""),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
