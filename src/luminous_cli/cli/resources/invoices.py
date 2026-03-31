"""Invoices resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._custom_fields import make_custom_fields_group
from luminous_cli.cli.resources._tags import make_tags_group

spec = ResourceSpec(
    name="invoices",
    singular="invoice",
    api_path="/invoices",
    columns=[
        ("ID", "id", "dim"),
        ("Status", "status", ""),
        ("Payment", "payment_status", ""),
        ("Customer", "customer.name", ""),
        ("Total", "total", "green"),
        ("Paid", "total_paid", "green"),
        ("Due", "total_due", "yellow"),
        ("Date", "order_date", ""),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
group.add_typer(make_tags_group("invoices"))
group.add_typer(make_custom_fields_group("invoices"))
