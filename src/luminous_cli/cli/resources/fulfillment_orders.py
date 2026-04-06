"""Fulfillment orders resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="fulfillment-orders",
    singular="fulfillment order",
    api_path="/fulfillment-orders",
    columns=[
        ("ID", "id", "dim"),
        ("Status", "status", ""),
        ("Order", "sales_order.order_number", "cyan"),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list"},
)

group = make_resource_group(spec)
