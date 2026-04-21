"""Products resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FormatOption, JsonOption, FileOption
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.cli.resources._tags import make_tags_group
from luminous_cli.cli.resources._custom_fields import make_custom_fields_group
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

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


@group.command("pricing")
def product_pricing(
    format: FormatOption = None,
) -> None:
    """Get pricing data for all products."""
    client = get_client()
    data = client.request("GET", "/products/pricing")
    render_json(data)


@group.command("company-pricing")
def product_company_pricing(
    format: FormatOption = None,
) -> None:
    """Get company-specific pricing for all products."""
    client = get_client()
    data = client.request("GET", "/products/company-pricing")
    render_json(data)


@group.command("get-pricing")
def product_get_pricing(
    product_id: int = typer.Argument(..., help="Product ID"),
    format: FormatOption = None,
) -> None:
    """Get pricing for a specific product."""
    client = get_client()
    data = client.request("GET", f"/products/{product_id}/pricing")
    render_json(data)


@group.command("get-company-pricing")
def product_get_company_pricing(
    product_id: int = typer.Argument(..., help="Product ID"),
    format: FormatOption = None,
) -> None:
    """Get company-specific pricing for a specific product."""
    client = get_client()
    data = client.request("GET", f"/products/{product_id}/company-pricing")
    render_json(data)


@group.command("add-alt-sku")
def add_alt_sku(
    product_id: int = typer.Argument(..., help="Product ID"),
    sku: str = typer.Argument(..., help="Alternate SKU to add"),
) -> None:
    """Add an alternate SKU to a product."""
    client = get_client()
    client.request("POST", f"/products/{product_id}/alternate-skus", json_body={"sku": sku})
    typer.echo(f"Added alternate SKU '{sku}' to product {product_id}")


@group.command("attach-boms")
def attach_boms(
    product_id: int = typer.Argument(..., help="Product ID"),
    bom_ids: str = typer.Argument(..., help="Comma-separated BOM IDs"),
) -> None:
    """Attach BOMs to a product."""
    ids = [int(x.strip()) for x in bom_ids.split(",")]
    client = get_client()
    client.request("POST", f"/products/{product_id}/boms", json_body={"bom_ids": ids})
    typer.echo(f"Attached {len(ids)} BOM(s) to product {product_id}")


@group.command("detach-boms")
def detach_boms(
    product_id: int = typer.Argument(..., help="Product ID"),
    bom_ids: str = typer.Argument(..., help="Comma-separated BOM IDs"),
) -> None:
    """Detach BOMs from a product."""
    ids = [int(x.strip()) for x in bom_ids.split(",")]
    client = get_client()
    client.request("DELETE", f"/products/{product_id}/boms", json_body={"bom_ids": ids})
    typer.echo(f"Detached {len(ids)} BOM(s) from product {product_id}")
