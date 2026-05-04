"""Units of measure resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="unit-of-measures",
    singular="unit of measure",
    api_path="/unit-of-measures",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Class", "unit_class_id", ""),
        ("Base", "base_unit", ""),
        ("Factor", "conversion_factor", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)
