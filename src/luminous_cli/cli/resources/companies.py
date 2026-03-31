"""Companies resource with subresources."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import (
    FilterOption,
    FormatOption,
    PageOption,
    PerPageOption,
    SortOption,
)
from luminous_cli.cli.resources._custom_fields import make_custom_fields_group
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._tags import make_tags_group
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

spec = ResourceSpec(
    name="companies",
    singular="company",
    api_path="/companies",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("City", "city", ""),
        ("State", "state", ""),
        ("Country", "country", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)
group.add_typer(make_tags_group("companies"))
group.add_typer(make_custom_fields_group("companies"))

# --- Subresources ---

contacts_app = typer.Typer(name="contacts", help="Company contacts")


@contacts_app.command("list")
def company_contacts(
    company_id: int = typer.Argument(..., help="Company ID"),
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List contacts for a company."""
    client = get_client()
    qp = QueryParams(page=page, per_page=per_page)
    resp = client.list(f"/companies/{company_id}/contacts", params=qp)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("Name", "first_name", ""),
        ("Last", "last_name", ""),
        ("Email", "email", "cyan"),
    ]
    render(resp.data, columns=columns, pagination=resp.pagination, fmt=fmt)


group.add_typer(contacts_app)

products_app = typer.Typer(name="products", help="Company products")


@products_app.command("list")
def company_products(
    company_id: int = typer.Argument(..., help="Company ID"),
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List products for a company."""
    client = get_client()
    qp = QueryParams(page=page, per_page=per_page)
    resp = client.list(f"/companies/{company_id}/products", params=qp)
    fmt = resolve_format(format)
    columns = [
        ("ID", "id", "dim"),
        ("SKU", "sku", "cyan"),
        ("Name", "name", ""),
    ]
    render(resp.data, columns=columns, pagination=resp.pagination, fmt=fmt)


group.add_typer(products_app)

price_overrides_app = typer.Typer(name="price-overrides", help="Company price overrides")


@price_overrides_app.command("list")
def company_price_overrides(
    company_id: int = typer.Argument(..., help="Company ID"),
    format: FormatOption = None,
) -> None:
    """List product price overrides for a company."""
    client = get_client()
    data = client.request("GET", f"/companies/{company_id}/product-price-overrides")
    result = data.get("data", data)
    if isinstance(result, dict):
        result = [result]
    fmt = resolve_format(format)
    columns = [
        ("Product ID", "product_id", "dim"),
        ("SKU", "sku", "cyan"),
        ("Price", "price", "green"),
    ]
    render(result, columns=columns, fmt=fmt)


group.add_typer(price_overrides_app)
