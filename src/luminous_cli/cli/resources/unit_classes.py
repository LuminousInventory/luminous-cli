"""Unit classes resource."""

from __future__ import annotations

import typer

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="unit-classes",
    singular="unit class",
    api_path="/unit-classes",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "name", "cyan"),
        ("Base Class", "base_class", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)


@group.command("set-default-uom")
def unit_classes_set_default_uom(
    unit_class_id: int = typer.Argument(..., help="Unit class ID"),
    unit_of_measure_id: int = typer.Argument(..., help="Unit of measure ID"),
) -> None:
    """Set the default (base) unit of measure for a unit class."""
    client = get_client()
    data = client.request(
        "POST",
        f"/unit-classes/{unit_class_id}/default-unit-of-measure/{unit_of_measure_id}",
    )
    render_json(data)
