"""Products resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._tags import make_tags_group
from luminous_cli.cli.resources._custom_fields import make_custom_fields_group

spec = ResourceSpec(
    name="products",
    singular="product",
    api_path="/products",
    columns=[
        ("ID", "id", "dim"),
        ("SKU", "sku", "cyan"),
        ("Name", "name", ""),
        ("Type", "type", ""),
        ("Retail", "retail_price", "green"),
        ("Wholesale", "wholesale_price", "green"),
        ("Sellable", "sellable", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "upsert", "delete"},
)

group = make_resource_group(spec)
group.add_typer(make_tags_group("products"))
group.add_typer(make_custom_fields_group("products"))
