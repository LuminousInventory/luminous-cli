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
]


def register_all(app: typer.Typer) -> None:
    """Register all resource command groups on the main app."""
    for group in ALL_GROUPS:
        app.add_typer(group)
