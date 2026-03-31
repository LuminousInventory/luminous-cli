"""Contacts resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="contacts",
    singular="contact",
    api_path="/contacts",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "full_name", ""),
        ("Email", "email", "cyan"),
        ("Phone", "phone_1", ""),
        ("Company", "company.name", ""),
        ("Primary", "is_primary", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)
