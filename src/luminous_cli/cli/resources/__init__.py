"""Resource command registration."""

from __future__ import annotations

import typer

from luminous_cli.cli.resources.boms import group as boms_group
from luminous_cli.cli.resources.companies import group as companies_group
from luminous_cli.cli.resources.contacts import group as contacts_group
from luminous_cli.cli.resources.inventory import group as inventory_group
from luminous_cli.cli.resources.invoices import group as invoices_group
from luminous_cli.cli.resources.locations import group as locations_group
from luminous_cli.cli.resources.price_levels import group as price_levels_group
from luminous_cli.cli.resources.price_schedules import group as price_schedules_group
from luminous_cli.cli.resources.products import group as products_group
from luminous_cli.cli.resources.purchase_orders import group as purchase_orders_group
from luminous_cli.cli.resources.receiving_reports import group as receiving_reports_group
from luminous_cli.cli.resources.sales_orders import group as sales_orders_group
from luminous_cli.cli.resources.transfer_orders import group as transfer_orders_group
from luminous_cli.cli.resources.warehouses import group as warehouses_group
from luminous_cli.cli.resources.stock_snapshot import group as stock_snapshot_group
from luminous_cli.cli.resources.consumption import group as consumption_group
from luminous_cli.cli.resources.inventory_aging import group as inventory_aging_group
from luminous_cli.cli.resources.bills import group as bills_group
from luminous_cli.cli.resources.forecast import group as forecast_group
from luminous_cli.cli.resources.reports import group as reports_group
from luminous_cli.cli.resources.currency import group as currency_group
from luminous_cli.cli.resources.fulfillment_orders import group as fulfillment_orders_group
from luminous_cli.cli.resources.payment_obligations import group as payment_obligations_group
from luminous_cli.cli.resources.prepayments import group as prepayments_group
from luminous_cli.cli.resources.vendor_credits import group as vendor_credits_group
from luminous_cli.cli.resources.vendor_returns import group as vendor_returns_group
from luminous_cli.cli.resources.integration_accounts import group as integration_accounts_group
from luminous_cli.cli.resources.integration_mappings import group as integration_field_mappings_group
from luminous_cli.cli.resources.integration_mappings import mappings_group as integration_mappings_group
from luminous_cli.cli.resources.warehouse_groups import group as warehouse_groups_group
from luminous_cli.cli.resources.labels import group as labels_group
from luminous_cli.cli.resources.inbound_shipments import group as inbound_shipments_group
from luminous_cli.cli.resources.purchase_order_shipments import group as purchase_order_shipments_group
from luminous_cli.cli.resources.custom_fields import group as custom_fields_group
from luminous_cli.cli.resources.suppliers import group as suppliers_group

ALL_GROUPS = [
    products_group,
    sales_orders_group,
    purchase_orders_group,
    inventory_group,
    transfer_orders_group,
    receiving_reports_group,
    invoices_group,
    companies_group,
    contacts_group,
    boms_group,
    locations_group,
    warehouses_group,
    price_schedules_group,
    price_levels_group,
    stock_snapshot_group,
    consumption_group,
    inventory_aging_group,
    bills_group,
    forecast_group,
    reports_group,
    currency_group,
    fulfillment_orders_group,
    payment_obligations_group,
    prepayments_group,
    vendor_credits_group,
    vendor_returns_group,
    integration_accounts_group,
    integration_field_mappings_group,
    integration_mappings_group,
    warehouse_groups_group,
    labels_group,
    inbound_shipments_group,
    purchase_order_shipments_group,
    custom_fields_group,
    suppliers_group,
]


def register_all(app: typer.Typer) -> None:
    """Register all resource command groups on the main app."""
    for group in ALL_GROUPS:
        app.add_typer(group)
