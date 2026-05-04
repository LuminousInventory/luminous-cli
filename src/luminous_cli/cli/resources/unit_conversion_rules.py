"""Unit conversion rules resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="unit-conversion-rules",
    singular="unit conversion rule",
    api_path="/unit-conversion-rules",
    columns=[
        ("ID", "id", "dim"),
        ("Type", "type", ""),
        ("Product", "product_id", ""),
        ("Base UOM", "base_unit_of_measure_id", ""),
        ("Converted UOM", "converted_unit_of_measure_id", ""),
        ("Factor", "conversion_factor", ""),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)


@group.command("resolve")
def ucr_resolve(
    product_id: int = typer.Option(..., "--product-id", help="Product ID"),
    base_unit_of_measure_id: int = typer.Option(
        ..., "--base-uom-id", help="Base unit of measure ID"
    ),
    converted_unit_of_measure_id: int = typer.Option(
        ..., "--converted-uom-id", help="Converted unit of measure ID"
    ),
    format: FormatOption = None,
) -> None:
    """Resolve the effective conversion rule for a product/UOM pair."""
    client = get_client()
    data = client.request(
        "GET",
        "/unit-conversion-rules/resolve",
        params={
            "product_id": str(product_id),
            "base_unit_of_measure_id": str(base_unit_of_measure_id),
            "converted_unit_of_measure_id": str(converted_unit_of_measure_id),
        },
    )
    render_json(data)
