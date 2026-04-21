"""Purchase order shipments resource."""

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group

spec = ResourceSpec(
    name="purchase-order-shipments",
    singular="purchase order shipment",
    api_path="/purchase-order-shipments",
    columns=[
        ("ID", "id", "dim"),
        ("PO ID", "purchase_order_id", ""),
        ("Status", "status", ""),
        ("Carrier", "carrier", ""),
        ("Tracking", "tracking_number", "cyan"),
        ("Ship Date", "ship_date", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get"},
)

group = make_resource_group(spec)
